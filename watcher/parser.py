"""
PARC binary format parser — PLACEHOLDER.

The actual PARC (Pearl Abyss Reflect Container) format has 76 data classes
and 531 mapped fields. Implementing this requires a real save file.

This module provides a placeholder that returns mock data,
and will be replaced with the real parser once we have a save file.
"""

from datetime import datetime, timezone


def parse_parc(decompressed_bytes: bytes) -> dict:
    """
    Parse PARC binary data into structured dict.
    Currently returns placeholder data — replace with real parser.
    """
    # TODO: Implement actual PARC parsing based on NattKh's save editor
    # Reference: https://github.com/NattKh/CRIMSON-DESERT-SAVE-EDITOR
    raise NotImplementedError(
        "PARC parser not yet implemented. "
        "Need a real save file to reverse-engineer the binary format."
    )


def generate_mock_data() -> dict:
    """Generate realistic mock save data for testing."""
    now = datetime.now(timezone.utc)
    return {
        "character": {
            "name": "Kliff",
            "level": 28,
            "playtime_seconds": 86400,
            "currency_silver": 52000,
            "stats": {"hp": 1500, "stamina": 900, "attack": 400, "defense": 320},
        },
        "inventory": [
            {"item_key": "ITEM_WEAPON_SWORD_SILVER", "name": "Silberklinge",
             "category": "Equipment", "stack_count": 1, "slot_index": 0},
            {"item_key": "ITEM_MAT_IRON_ORE", "name": "Eisenerz",
             "category": "Material", "stack_count": 63, "slot_index": 1},
            {"item_key": "ITEM_CONS_POTION_HEALTH", "name": "Heiltrank",
             "category": "Consumable", "stack_count": 15, "slot_index": 2},
        ],
        "equipment": [
            {"item_key": "ITEM_WEAPON_SWORD_SILVER", "name": "Silberklinge",
             "slot_type": "weapon", "enchant_level": 7, "endurance": 82, "sharpness": 68},
            {"item_key": "ITEM_ARMOR_CHEST_CHAIN", "name": "Kettenhemd",
             "slot_type": "chest", "enchant_level": 4, "endurance": 91, "sharpness": 100},
        ],
        "quests": [
            {"quest_key": "QUEST_MAIN_CH1_GREYMANE", "name": "Die Greymanes vereinen",
             "status": "completed", "completed_at": now.isoformat()},
            {"quest_key": "QUEST_SIDE_BLACKSMITH", "name": "Der Schmied von Alcyon",
             "status": "active", "completed_at": None},
        ],
        "mercenaries": [
            {"merc_key": "MERC_OONGKA", "name": "Oongka", "type": "companion", "custom_name": None},
        ],
        "save_meta": {
            "slot": "slot100",
            "timestamp": now.isoformat(),
            "game_version": "1.01.02",
        },
    }
