"""
PARC binary format parser for Crimson Desert save files.

Uses the real save_parser.py (extracted from CrimsonSaveEditor)
to parse the decompressed PARC data into structured game data.

Pipeline: save.save → crypto.decrypt_save() → parser.parse_parc()
"""

import json
from pathlib import Path

import save_parser


# ── Load data files ──────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent / "data"


def _load_item_lookup() -> dict[int, dict]:
    """Load item names — prefer German (item_names_de.json), fallback to English."""
    try:
        # Try German first
        de_path = DATA_DIR / "item_names_de.json"
        en_path = DATA_DIR / "item_names.json"
        path = de_path if de_path.exists() else en_path

        data = json.loads(path.read_text())
        items = data.get("items", data) if isinstance(data, dict) else data
        lookup = {}
        for item in items:
            entry = dict(item)
            # Use German name if available, otherwise English
            if "name_de" in entry:
                entry["name"] = entry["name_de"]
            lookup[item["itemKey"]] = entry
        print(f"  Items geladen: {len(lookup)} ({'DE' if de_path.exists() else 'EN'})")
        return lookup
    except Exception as e:
        print(f"  WARNUNG: Item-Daten nicht geladen: {e}")
        return {}


def _load_quest_lookup() -> dict[int, str]:
    """Load quest names — prefer German (quest_names_de.json), fallback to English."""
    try:
        de_path = DATA_DIR / "quest_names_de.json"
        en_path = DATA_DIR / "quest_names.json"
        path = de_path if de_path.exists() else en_path

        data = json.loads(path.read_text())
        if isinstance(data, list):
            lookup = {}
            for q in data:
                # Prefer German display/name
                name = q.get("display_de", q.get("name_de", q.get("display", q.get("name", "?"))))
                lookup[q["key"]] = name
            print(f"  Quests geladen: {len(lookup)} ({'DE' if de_path.exists() else 'EN'})")
            return lookup
        return {}
    except Exception as e:
        print(f"  WARNUNG: Quest-Daten nicht geladen: {e}")
        return {}


def _load_mission_lookup() -> dict[int, str]:
    """Load mission names — German not yet available, use English."""
    try:
        data = json.loads((DATA_DIR / "mission_names.json").read_text())
        if isinstance(data, list):
            return {m["key"]: m.get("display", m.get("name", "?")) for m in data}
        return {}
    except Exception:
        return {}


# Load EN→DE translation map for anything not covered by specific files
def _load_translation_map() -> dict[str, str]:
    """Load translation_en_de.json for general EN→DE lookups."""
    try:
        path = DATA_DIR / "translation_en_de.json"
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return {}


ITEM_LOOKUP = _load_item_lookup()
QUEST_LOOKUP = _load_quest_lookup()
MISSION_LOOKUP = _load_mission_lookup()
EN_DE_MAP = _load_translation_map()


# ── Equipment slot mapping ───────────────────────────────────────────────────

EQUIP_SLOTS = {
    0: "main_weapon",
    1: "sub_weapon",
    2: "ranged_weapon",
    4: "chest",
    5: "gloves",
    6: "boots",
    12: "melee_secondary",
    13: "fist_weapon",
    15: "lantern",
    16: "cloak",
    20: "accessory",
}


# ── Main parser ──────────────────────────────────────────────────────────────

def parse_parc(decompressed_bytes: bytes) -> dict:
    """
    Parse PARC binary data into structured dict for the dashboard.

    Returns dict with keys:
      - character: {level, hp, mp, characterKey, factionKey}
      - equipment: [{name, category, slot, slot_name, sharpness, endurance, ...}]
      - inventory: [{name, category, slot, stack, ...}]
      - quests: {total, completed, active, states}
      - missions: {total, states}
      - mercenaries: {}
      - schema_info: {type_count, object_count}
    """
    raw = bytes(decompressed_bytes)
    load_meta = {"source": "watcher"}

    result = save_parser.build_result_from_raw(raw, load_meta, include_legacy=True)

    # ── Character stats ──────────────────────────────────────────────────
    char = result.get("character")
    character = {}
    if char and char.found:
        character = {
            "level": char.level,
            "characterKey": char.characterKey,
            "factionKey": char.factionKey,
            "currentHp": char.currentHp,
            "currentMp": char.currentMp,
            "bitmask": char.bitmask,
        }

    # ── Items (equipment + inventory) ────────────────────────────────────
    items_raw = result.get("items", [])
    equipment = []
    inventory = []

    for item in items_raw:
        info = ITEM_LOOKUP.get(item.itemKey, {})
        item_data = {
            "itemNo": item.itemNo,
            "itemKey": item.itemKey,
            "name": info.get("name", f"Unknown ({item.itemKey})"),
            "category": info.get("category", "Unknown"),
            "internalName": info.get("internalName", ""),
            "slot": item.slot,
            "slot_name": EQUIP_SLOTS.get(item.slot, f"slot_{item.slot}"),
            "stack": item.stack,
            "enchant": item.enchant,
            "sharpness": item.sharpness,
            "endurance": item.endurance,
            "source": item.source,
        }

        if item.source == "Equipment":
            equipment.append(item_data)
        else:
            inventory.append(item_data)

    # If all items are from Equipment source, split by section
    if not inventory and items_raw:
        # Section 0 = equipped, section 1+ = inventory
        equipped = [i for i in equipment if any(
            ir.section == 0 for ir in items_raw if ir.itemNo == i["itemNo"]
        )]
        inv = [i for i in equipment if i not in equipped]
        if inv:
            equipment = equipped
            inventory = inv

    # ── Quests & Missions ────────────────────────────────────────────────
    quest_data = {"total": 0, "completed": 0, "active": 0, "states": []}
    mission_data = {"total": 0, "completed": 0, "active": 0, "states": []}

    STATE_MAP = {0: "none", 1: "active", 2: "completed", 3: "failed", 4: "branched"}

    for obj in result.get("objects", []):
        if obj.class_name != "QuestSaveData":
            continue

        for field_name, key_field, data_target, lookup in [
            ("_questStateList", "_questKey", quest_data, QUEST_LOOKUP),
            ("_missionStateList", "_key", mission_data, MISSION_LOOKUP),
        ]:
            target_field = None
            for f in obj.fields:
                if f.name == field_name:
                    target_field = f
                    break
            if not target_field or not target_field.list_elements:
                continue

            for elem in target_field.list_elements:
                key_val = None
                state_val = None
                for cf in elem.child_fields:
                    if cf.name == key_field:
                        key_val = cf.value_repr
                    elif cf.name == "_state":
                        state_val = cf.value_repr

                try:
                    state_int = int(state_val) if state_val is not None else -1
                except (ValueError, TypeError):
                    state_int = -1
                state_name = STATE_MAP.get(state_int, f"unknown({state_val})")

                if state_name == "completed":
                    data_target["completed"] += 1
                elif state_name == "active":
                    data_target["active"] += 1

                try:
                    key_int = int(key_val) if key_val is not None else 0
                except (ValueError, TypeError):
                    key_int = 0
                name = lookup.get(key_int, f"ID_{key_val}")

                if state_name in ("completed", "active"):
                    data_target["states"].append({
                        "key": key_int,
                        "name": name,
                        "status": state_name,
                    })

            data_target["total"] = len(target_field.list_elements)

    # ── Mercenaries ──────────────────────────────────────────────────────
    mercenary_data = {}
    for obj in result.get("objects", []):
        if obj.class_name == "MercenaryClanSaveData":
            mercenary_data["found"] = True
            mercenary_data["data_size"] = obj.data_size

    # ── Schema info ──────────────────────────────────────────────────────
    schema_info = {
        "type_count": len(result.get("schema", {}).get("types", [])),
        "object_count": len(result.get("objects", [])),
        "toc_entries": result.get("toc", {}).get("entry_count", 0),
    }

    return {
        "character": character,
        "equipment": equipment,
        "inventory": inventory,
        "quests": quest_data,
        "missions": mission_data,
        "mercenaries": mercenary_data,
        "schema_info": schema_info,
    }
