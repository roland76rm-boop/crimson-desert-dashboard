"""
Seed-Script: Generates 10 realistic mock snapshots for frontend development.
Usage: python seed_mock.py
"""

import asyncio
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone

from database import Base, engine, async_session
from models import Snapshot, InventorySnapshot, EquipmentSnapshot, QuestSnapshot, Item

# --- Item catalog ---

ITEMS = [
    ("ITEM_WEAPON_SWORD_STEEL", "Stählernes Schwert", "Equipment"),
    ("ITEM_WEAPON_SWORD_SILVER", "Silberklinge", "Equipment"),
    ("ITEM_WEAPON_BOW_HUNTING", "Jagdbogen", "Equipment"),
    ("ITEM_WEAPON_STAFF_OAK", "Eichenstab", "Equipment"),
    ("ITEM_ARMOR_HELM_IRON", "Eisenhelm", "Equipment"),
    ("ITEM_ARMOR_CHEST_LEATHER", "Lederrüstung", "Equipment"),
    ("ITEM_ARMOR_CHEST_CHAIN", "Kettenhemd", "Equipment"),
    ("ITEM_ARMOR_LEGS_LEATHER", "Lederhose", "Equipment"),
    ("ITEM_ARMOR_BOOTS_IRON", "Eisenstiefel", "Equipment"),
    ("ITEM_ARMOR_GLOVES_LEATHER", "Lederhandschuhe", "Equipment"),
    ("ITEM_SHIELD_WOODEN", "Holzschild", "Equipment"),
    ("ITEM_RING_RUBY", "Rubinring", "Equipment"),
    ("ITEM_AMULET_WOLF", "Wolfs-Amulett", "Equipment"),
    ("ITEM_MAT_IRON_ORE", "Eisenerz", "Material"),
    ("ITEM_MAT_SILVER_ORE", "Silbererz", "Material"),
    ("ITEM_MAT_WOOD_OAK", "Eichenholz", "Material"),
    ("ITEM_MAT_LEATHER_RAW", "Rohleder", "Material"),
    ("ITEM_MAT_HERB_HEAL", "Heilkraut", "Material"),
    ("ITEM_MAT_CLOTH_SILK", "Seidenstoff", "Material"),
    ("ITEM_MAT_STONE_GRANITE", "Granit", "Material"),
    ("ITEM_CONS_POTION_HEALTH", "Heiltrank", "Consumable"),
    ("ITEM_CONS_POTION_STAMINA", "Ausdauertrank", "Consumable"),
    ("ITEM_CONS_POTION_ATTACK", "Angriffselixier", "Consumable"),
    ("ITEM_CONS_FOOD_BREAD", "Brot", "Consumable"),
    ("ITEM_CONS_FOOD_MEAT", "Gebratenes Fleisch", "Consumable"),
    ("ITEM_CONS_FOOD_STEW", "Kräftiger Eintopf", "Consumable"),
    ("ITEM_QUEST_LETTER_GREYMANE", "Brief der Greymanes", "Quest"),
    ("ITEM_QUEST_KEY_DUNGEON", "Verlieschlüssel", "Quest"),
    ("ITEM_QUEST_MAP_TREASURE", "Schatzkarte", "Quest"),
    ("ITEM_MISC_GEM_EMERALD", "Smaragd", "Misc"),
    ("ITEM_MISC_GEM_SAPPHIRE", "Saphir", "Misc"),
    ("ITEM_MISC_TROPHY_WOLF", "Wolfszahn", "Misc"),
]

EQUIPMENT_SLOTS = [
    ("ITEM_WEAPON_SWORD_STEEL", "Stählernes Schwert", "weapon"),
    ("ITEM_ARMOR_HELM_IRON", "Eisenhelm", "helm"),
    ("ITEM_ARMOR_CHEST_LEATHER", "Lederrüstung", "chest"),
    ("ITEM_ARMOR_LEGS_LEATHER", "Lederhose", "legs"),
    ("ITEM_ARMOR_BOOTS_IRON", "Eisenstiefel", "boots"),
    ("ITEM_ARMOR_GLOVES_LEATHER", "Lederhandschuhe", "gloves"),
    ("ITEM_SHIELD_WOODEN", "Holzschild", "offhand"),
    ("ITEM_RING_RUBY", "Rubinring", "ring"),
    ("ITEM_AMULET_WOLF", "Wolfs-Amulett", "amulet"),
]

QUESTS = [
    ("QUEST_MAIN_CH1_GREYMANE", "Die Greymanes vereinen"),
    ("QUEST_MAIN_CH1_VILLAGE", "Das verlorene Dorf"),
    ("QUEST_MAIN_CH2_CASTLE", "Die Burg von Alcyon"),
    ("QUEST_MAIN_CH2_DRAGON", "Drachens Erwachen"),
    ("QUEST_SIDE_BLACKSMITH", "Der Schmied von Alcyon"),
    ("QUEST_SIDE_HERBALIST", "Die Kräutersammlerin"),
    ("QUEST_SIDE_HUNTER", "Wolfsjagd"),
    ("QUEST_SIDE_MERCHANT", "Handelsroute sichern"),
    ("QUEST_SIDE_MINE", "Die verlassene Mine"),
    ("QUEST_SIDE_RUINS", "Ruinen der Alten"),
    ("QUEST_SIDE_BANDITS", "Banditenlager ausräuchern"),
    ("QUEST_SIDE_MESSENGER", "Botendienst"),
]

MERCENARIES = [
    ("MERC_OONGKA", "Oongka", "companion"),
    ("MERC_SAYA", "Saya", "companion"),
    ("MERC_WOLF_GREY", "Grauer Wolf", "pet"),
    ("MERC_HORSE_BLACK", "Schwarzer Hengst", "mount"),
    ("MERC_HAWK", "Falke", "pet"),
]

# Equipment upgrade paths per snapshot
EQUIP_UPGRADES = [
    {},
    {},
    {"weapon": ("ITEM_WEAPON_SWORD_SILVER", "Silberklinge")},
    {},
    {"chest": ("ITEM_ARMOR_CHEST_CHAIN", "Kettenhemd")},
    {},
    {},
    {"weapon": ("ITEM_WEAPON_BOW_HUNTING", "Jagdbogen")},
    {},
    {},
]


def build_snapshot(index: int, base_time: datetime) -> dict:
    """Build snapshot data for index 0-9, progressing over time."""
    t = base_time + timedelta(days=index, hours=random.randint(0, 12), minutes=random.randint(0, 59))
    level = 12 + index * 3 + random.randint(-1, 1)
    playtime = 28800 + index * 7200 + random.randint(-1800, 1800)  # ~8h start, +2h per snapshot
    silver = 15000 + index * 8000 + random.randint(-2000, 3000)

    hp = 800 + level * 25 + random.randint(-20, 20)
    stamina = 500 + level * 15 + random.randint(-10, 10)
    attack = 150 + level * 12 + random.randint(-10, 15)
    defense = 120 + level * 10 + random.randint(-10, 10)

    # Inventory grows over time
    num_items = 8 + index * 3 + random.randint(0, 4)
    inventory = []
    used_slots = set()
    for i in range(min(num_items, len(ITEMS))):
        key, name, cat = ITEMS[i]
        slot = i
        stack = 1 if cat == "Equipment" else random.randint(1, 50 + index * 5)
        inventory.append({
            "item_key": key, "name": name, "category": cat,
            "stack_count": stack, "slot_index": slot,
        })

    # Equipment with gradual upgrades
    equipment = []
    current_equip = {}
    for ek, en, eslot in EQUIPMENT_SLOTS:
        current_equip[eslot] = (ek, en)
    for prev_idx in range(index + 1):
        for slot, (ek, en) in EQUIP_UPGRADES[prev_idx].items():
            current_equip[slot] = (ek, en)
    for eslot, (ek, en) in current_equip.items():
        enchant = min(index // 2 + random.randint(0, 2), 10)
        endurance = max(50, 100 - index * 2 + random.randint(-5, 5))
        sharpness = max(40, 95 - index * 3 + random.randint(-5, 10))
        equipment.append({
            "item_key": ek, "name": en, "slot_type": eslot,
            "enchant_level": enchant, "endurance": endurance, "sharpness": sharpness,
        })

    # Quests: more completed over time
    completed_count = min(2 + index, len(QUESTS))
    quests = []
    for qi, (qk, qn) in enumerate(QUESTS):
        if qi < completed_count:
            ct = t - timedelta(hours=random.randint(1, 48))
            quests.append({"quest_key": qk, "name": qn, "status": "completed", "completed_at": ct.isoformat()})
        elif qi < completed_count + 3:
            quests.append({"quest_key": qk, "name": qn, "status": "active", "completed_at": None})

    # Mercenaries: unlock over time
    merc_count = min(1 + index // 2, len(MERCENARIES))
    mercenaries = [
        {"merc_key": mk, "name": mn, "type": mt, "custom_name": None}
        for mk, mn, mt in MERCENARIES[:merc_count]
    ]

    slot_num = 100 + (index % 3)
    return {
        "character": {
            "name": "Kliff",
            "level": level,
            "playtime_seconds": playtime,
            "currency_silver": silver,
            "stats": {"hp": hp, "stamina": stamina, "attack": attack, "defense": defense},
        },
        "inventory": inventory,
        "equipment": equipment,
        "quests": quests,
        "mercenaries": mercenaries,
        "save_meta": {
            "slot": f"slot{slot_num}",
            "timestamp": t.isoformat(),
            "game_version": "1.01.02",
        },
    }


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    base_time = datetime(2026, 3, 20, 18, 0, 0, tzinfo=timezone.utc)

    async with async_session() as db:
        # Seed items table
        for key, name, cat in ITEMS:
            item = Item(item_key=key, name=name, category=cat)
            await db.merge(item)

        # Seed snapshots
        for i in range(10):
            data = build_snapshot(i, base_time)
            raw_json = json.dumps(data, sort_keys=True)
            checksum = hashlib.sha256(raw_json.encode()).hexdigest()

            ts = datetime.fromisoformat(data["save_meta"]["timestamp"])
            snap = Snapshot(
                uploaded_at=ts + timedelta(seconds=30),
                save_slot=data["save_meta"]["slot"],
                save_timestamp=ts,
                character_name=data["character"]["name"],
                character_level=data["character"]["level"],
                playtime_seconds=data["character"]["playtime_seconds"],
                currency_silver=data["character"]["currency_silver"],
                raw_data=data,
                checksum=checksum,
            )
            db.add(snap)
            await db.flush()

            for inv in data["inventory"]:
                db.add(InventorySnapshot(
                    snapshot_id=snap.id, item_key=inv["item_key"],
                    item_name=inv["name"], stack_count=inv["stack_count"],
                    slot_index=inv["slot_index"],
                ))

            for eq in data["equipment"]:
                db.add(EquipmentSnapshot(
                    snapshot_id=snap.id, item_key=eq["item_key"],
                    item_name=eq["name"], enchant_level=eq["enchant_level"],
                    endurance=eq["endurance"], sharpness=eq["sharpness"],
                    slot_type=eq["slot_type"],
                ))

            for q in data["quests"]:
                ca = datetime.fromisoformat(q["completed_at"]) if q["completed_at"] else None
                db.add(QuestSnapshot(
                    snapshot_id=snap.id, quest_key=q["quest_key"],
                    quest_name=q["name"], status=q["status"],
                    completed_at=ca,
                ))

        await db.commit()
        print(f"Seeded 10 snapshots, {len(ITEMS)} items.")


if __name__ == "__main__":
    asyncio.run(seed())
