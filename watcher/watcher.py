"""
Crimson Desert Save File Watcher.
Monitors save directory for changes, parses save files, uploads to backend API.
Supports mock mode for development without the game installed.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from parser import generate_mock_data

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
            return base  # Will fail later, but that's OK for mock mode
        # Find first steam ID directory
        for d in base.iterdir():
            if d.is_dir() and d.name.isdigit():
                log.info(f"Auto-detected Steam ID: {d.name}")
                return d
        return base
    else:
        return base / steam_id


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
            # TODO: Replace with real crypto + parser pipeline
            # from crypto import decrypt_save
            # from parser import parse_parc
            # raw = Path(filepath).read_bytes()
            # decompressed = decrypt_save(raw)
            # data = parse_parc(decompressed)

            # For now, use mock data
            log.warning("Using mock data (PARC parser not yet implemented)")
            data = generate_mock_data()

            upload_snapshot(
                self.config["api_endpoint"],
                self.config["api_key"],
                data,
            )
        except Exception as e:
            log.error(f"Failed to process save: {e}")


def run_mock_mode(config: dict):
    """Upload a single mock snapshot (for testing without the game)."""
    log.info("Running in MOCK MODE — uploading test data")
    data = generate_mock_data()
    success = upload_snapshot(config["api_endpoint"], config["api_key"], data)
    if success:
        log.info("Mock upload complete")
    else:
        log.error("Mock upload failed")


def main():
    config = load_config()
    log.info("Crimson Desert Save Watcher starting...")

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
