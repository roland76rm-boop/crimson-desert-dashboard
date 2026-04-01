"""
Crimson Desert Save File Watcher.
Monitors save directory for changes, decrypts + parses save files, uploads to backend API.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from crypto import decrypt_save, DecryptionError
from parser import parse_parc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("cd-watcher")


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        log.error("config.json not found")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def find_save_directory(config: dict) -> Path:
    """Resolve save directory, auto-detecting steam_id if needed."""
    base = Path(config["save_directory"])
    steam_id = config.get("steam_id", "auto")

    if steam_id == "auto":
        if not base.exists():
            return base
        for d in base.iterdir():
            if d.is_dir() and d.name.isdigit():
                log.info(f"Auto-detected Steam ID: {d.name}")
                return d
        return base
    else:
        return base / steam_id


def format_payload(parsed: dict, filepath: str) -> dict:
    """Convert parser output to backend UploadPayload format."""
    char = parsed.get("character", {})
    now = datetime.now(timezone.utc)

    # Extract slot from path (e.g., .../slot0/save.save → slot0)
    path = Path(filepath)
    slot = path.parent.name if path.parent.name.startswith("slot") else "unknown"

    return {
        "character": {
            "name": "Kliff",  # PARC doesn't store name as plain text; Kliff is the protagonist
            "level": char.get("level", 0),
            "playtime_seconds": 0,  # Not directly in CharacterStatusSaveData
            "currency_silver": 0,   # Would need to scan inventory for silver item
            "stats": {
                "hp": char.get("currentHp", 0),
                "stamina": 0,
                "attack": 0,
                "defense": 0,
            },
        },
        "inventory": [
            {
                "item_key": str(item["itemKey"]),
                "name": item["name"],
                "category": item["category"],
                "stack_count": item["stack"],
                "slot_index": item["slot"],
            }
            for item in parsed.get("inventory", [])
        ],
        "equipment": [
            {
                "item_key": str(item["itemKey"]),
                "name": item["name"],
                "slot_type": item["slot_name"],
                "enchant_level": item["enchant"],
                "endurance": item["endurance"],
                "sharpness": item["sharpness"],
            }
            for item in parsed.get("equipment", [])
        ],
        "quests": [
            {
                "quest_key": str(q["key"]),
                "name": q["name"],
                "status": q["status"],
                "completed_at": now.isoformat() if q["status"] == "completed" else None,
            }
            for q in parsed.get("quests", {}).get("states", [])
        ],
        "mercenaries": [],
        "save_meta": {
            "slot": slot,
            "timestamp": now.isoformat(),
            "game_version": "1.0",
        },
    }


def upload_snapshot(endpoint: str, api_key: str, data: dict) -> bool:
    """Upload parsed save data to the backend API."""
    try:
        resp = requests.post(
            endpoint,
            json=data,
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            timeout=30,
        )
        if resp.status_code == 201:
            result = resp.json()
            if result.get("status") == "duplicate":
                log.info("Snapshot already uploaded (duplicate)")
            else:
                log.info(f"Uploaded snapshot #{result.get('snapshot_id')}")
            return True
        else:
            log.error(f"Upload failed: {resp.status_code} — {resp.text}")
            return False
    except requests.RequestException as e:
        log.error(f"Upload error: {e}")
        return False


class SaveFileHandler(FileSystemEventHandler):
    """Handles file system events for save files."""

    def __init__(self, config: dict):
        self.config = config
        self.last_processed = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith("save.save"):
            return

        # Debounce: skip if processed within last 5 seconds
        now = time.time()
        if now - self.last_processed.get(event.src_path, 0) < 5:
            return
        self.last_processed[event.src_path] = now

        log.info(f"Save file changed: {event.src_path}")
        self.process_save(event.src_path)

    def process_save(self, filepath: str):
        """Process a save file: decrypt → parse → upload."""
        try:
            p = Path(filepath)
            if not p.exists():
                log.debug(f"File gone (temp rename by game), skipping: {filepath}")
                return
            # Small delay — game may still be writing
            time.sleep(0.5)
            raw = p.read_bytes()
            log.info(f"Read {len(raw):,} bytes from {filepath}")

            # Decrypt (ChaCha20 + LZ4)
            decompressed = decrypt_save(raw)
            log.info(f"Decrypted → {len(decompressed):,} bytes PARC data")

            # Parse PARC binary
            parsed = parse_parc(decompressed)
            char = parsed.get("character", {})
            equip_count = len(parsed.get("equipment", []))
            inv_count = len(parsed.get("inventory", []))
            log.info(
                f"Parsed: Level {char.get('level', '?')}, "
                f"{equip_count} equipment, {inv_count} inventory items"
            )

            # Format for backend API
            payload = format_payload(parsed, filepath)

            # Upload
            upload_snapshot(
                self.config["api_endpoint"],
                self.config["api_key"],
                payload,
            )
        except DecryptionError as e:
            log.error(f"Decryption failed: {e}")
        except Exception as e:
            log.error(f"Failed to process save: {e}", exc_info=True)


def run_mock_mode(config: dict):
    """Process the test save file (for testing without the game running)."""
    test_save = Path(__file__).parent / "test_save.save"
    if test_save.exists():
        log.info(f"MOCK MODE — processing test save: {test_save}")
        try:
            raw = test_save.read_bytes()
            decompressed = decrypt_save(raw)
            parsed = parse_parc(decompressed)
            payload = format_payload(parsed, str(test_save))

            log.info(f"Parsed: Level {parsed['character'].get('level')}, "
                     f"{len(parsed['equipment'])} equipment")

            success = upload_snapshot(config["api_endpoint"], config["api_key"], payload)
            if success:
                log.info("Mock upload complete")
            else:
                log.error("Mock upload failed")
        except Exception as e:
            log.error(f"Mock mode failed: {e}", exc_info=True)
    else:
        log.error(f"No test save file at {test_save}")


def main():
    config = load_config()
    log.info("Crimson Desert Save Watcher starting...")
    log.info("Pipeline: SAVE header → ChaCha20 decrypt → LZ4 decompress → PARC parse")

    if config.get("mock_mode", False):
        run_mock_mode(config)
        return

    save_dir = find_save_directory(config)
    if not save_dir.exists():
        log.error(f"Save directory not found: {save_dir}")
        log.info("Is the game installed? Set mock_mode=true for testing.")
        sys.exit(1)

    log.info(f"Watching: {save_dir}")
    handler = SaveFileHandler(config)
    observer = Observer()
    observer.schedule(handler, str(save_dir), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(config.get("watch_interval_seconds", 5))
    except KeyboardInterrupt:
        log.info("Stopping watcher...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
