from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --- Upload (from watcher) ---

class UploadStats(BaseModel):
    hp: int = 0
    stamina: int = 0
    attack: int = 0
    defense: int = 0


class UploadCharacter(BaseModel):
    name: str
    level: int
    playtime_seconds: int
    currency_silver: int
    stats: UploadStats = UploadStats()


class UploadInventoryItem(BaseModel):
    item_key: str
    name: str
    category: str = "Unknown"
    stack_count: int = 1
    slot_index: int = 0


class UploadEquipmentItem(BaseModel):
    item_key: str
    name: str
    slot_type: str
    enchant_level: int = 0
    endurance: int = 100
    sharpness: int = 100


class UploadQuest(BaseModel):
    quest_key: str
    name: str
    status: str = "active"
    completed_at: Optional[datetime] = None


class UploadMercenary(BaseModel):
    merc_key: str
    name: str
    type: str = "companion"
    custom_name: Optional[str] = None


class UploadSaveMeta(BaseModel):
    slot: str
    timestamp: datetime
    game_version: str = "unknown"


class UploadPayload(BaseModel):
    character: UploadCharacter
    inventory: list[UploadInventoryItem] = []
    equipment: list[UploadEquipmentItem] = []
    quests: list[UploadQuest] = []
    mercenaries: list[UploadMercenary] = []
    save_meta: UploadSaveMeta


# --- Response models ---

class SnapshotSummary(BaseModel):
    id: int
    uploaded_at: datetime
    save_slot: Optional[str]
    character_name: Optional[str]
    character_level: Optional[int]
    playtime_seconds: Optional[int]
    currency_silver: Optional[int]

    class Config:
        from_attributes = True


class SnapshotDetail(SnapshotSummary):
    save_timestamp: Optional[datetime]
    raw_data: Optional[dict]

    class Config:
        from_attributes = True


class CharacterResponse(BaseModel):
    name: Optional[str]
    level: Optional[int]
    playtime_seconds: Optional[int]
    currency_silver: Optional[int]
    stats: dict = {}
    snapshot_id: int
    uploaded_at: datetime


class InventoryItemResponse(BaseModel):
    item_key: str
    item_name: Optional[str]
    stack_count: int
    slot_index: int
    category: str = "Unknown"

    class Config:
        from_attributes = True


class EquipmentItemResponse(BaseModel):
    item_key: str
    item_name: Optional[str]
    enchant_level: int
    endurance: int
    sharpness: int
    slot_type: str

    class Config:
        from_attributes = True


class QuestResponse(BaseModel):
    quest_key: str
    quest_name: Optional[str]
    status: str
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class MercenaryResponse(BaseModel):
    merc_key: str
    name: str
    type: str
    custom_name: Optional[str]


class TimelinePoint(BaseModel):
    uploaded_at: datetime
    character_level: Optional[int]
    currency_silver: Optional[int]
    playtime_seconds: Optional[int]
    inventory_count: int = 0
    quests_completed: int = 0
