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
    """Load item_names.json → {itemKey: {name, category, internalName}}"""
    try:
        data = json.loads((DATA_DIR / "item_names.json").read_text())
        items = data.get("items", [])
        return {item["itemKey"]: item for item in items}
    except Exception:
        return {}


def _load_quest_lookup() -> dict[str, str]:
    """Load quest_names.json → {questKey: name}"""
    try:
        return json.loads((DATA_DIR / "quest_names.json").read_text())
    except Exception:
        return {}


def _load_mission_lookup() -> dict[str, str]:
    """Load mission_names.json → {missionKey: name}"""
    try:
        return json.loads((DATA_DIR / "mission_names.json").read_text())
    except Exception:
        return {}


ITEM_LOOKUP = _load_item_lookup()
QUEST_LOOKUP = _load_quest_lookup()
MISSION_LOOKUP = _load_mission_lookup()


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
    mission_data = {"total": 0, "states": []}

    for obj in result.get("objects", []):
        if obj.class_name == "QuestSaveData":
            for field in obj.fields:
                if field.name == "_questStateList" and field.present:
                    # count from value_repr
                    if "count=" in (field.value_repr or ""):
                        count_str = field.value_repr.split("count=")[1].split()[0]
                        quest_data["total"] = int(count_str)
                if field.name == "_missionStateList" and field.present:
                    if "count=" in (field.value_repr or ""):
                        count_str = field.value_repr.split("count=")[1].split()[0]
                        mission_data["total"] = int(count_str)

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
