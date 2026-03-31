from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database import Base


class Snapshot(Base):
    __tablename__ = "cd_snapshots"

    id = Column(Integer, primary_key=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    save_slot = Column(String(20))
    save_timestamp = Column(DateTime(timezone=True))
    character_name = Column(String(100))
    character_level = Column(Integer)
    playtime_seconds = Column(BigInteger)
    currency_silver = Column(BigInteger)
    raw_data = Column(JSONB)
    checksum = Column(String(64))

    __table_args__ = (
        Index("idx_cd_snapshots_uploaded", uploaded_at.desc()),
        Index("idx_cd_snapshots_checksum", checksum),
    )


class Item(Base):
    __tablename__ = "cd_items"

    item_key = Column(String(200), primary_key=True)
    name = Column(String(300))
    category = Column(String(100))
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class InventorySnapshot(Base):
    __tablename__ = "cd_inventory_snapshots"

    id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey("cd_snapshots.id", ondelete="CASCADE"))
    item_key = Column(String(200))
    item_name = Column(String(300))
    stack_count = Column(Integer)
    slot_index = Column(Integer)


class EquipmentSnapshot(Base):
    __tablename__ = "cd_equipment_snapshots"

    id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey("cd_snapshots.id", ondelete="CASCADE"))
    item_key = Column(String(200))
    item_name = Column(String(300))
    enchant_level = Column(Integer)
    endurance = Column(Integer)
    sharpness = Column(Integer)
    slot_type = Column(String(50))


class QuestSnapshot(Base):
    __tablename__ = "cd_quest_snapshots"

    id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey("cd_snapshots.id", ondelete="CASCADE"))
    quest_key = Column(String(200))
    quest_name = Column(String(300))
    status = Column(String(50))
    completed_at = Column(DateTime(timezone=True))
