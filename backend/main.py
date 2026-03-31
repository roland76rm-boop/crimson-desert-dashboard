import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import Base, engine, get_db
from models import Snapshot, InventorySnapshot, EquipmentSnapshot, QuestSnapshot, Item
from schemas import (
    UploadPayload,
    SnapshotSummary,
    SnapshotDetail,
    CharacterResponse,
    InventoryItemResponse,
    EquipmentItemResponse,
    QuestResponse,
    MercenaryResponse,
    TimelinePoint,
)

settings = get_settings()

app = FastAPI(title="Crimson Desert Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- Auth helper ---

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")


# --- Helper to get latest snapshot ---

async def _latest_snapshot(db: AsyncSession) -> Optional[Snapshot]:
    result = await db.execute(
        select(Snapshot).order_by(desc(Snapshot.uploaded_at)).limit(1)
    )
    return result.scalar_one_or_none()


# --- Endpoints ---

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "crimson-desert-api"}


@app.post("/api/upload", status_code=201)
async def upload_save(
    payload: UploadPayload,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    raw = payload.model_dump(mode="json")
    checksum = hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()

    existing = await db.execute(select(Snapshot).where(Snapshot.checksum == checksum))
    if existing.scalar_one_or_none():
        return {"status": "duplicate", "message": "Snapshot already exists"}

    snapshot = Snapshot(
        save_slot=payload.save_meta.slot,
        save_timestamp=payload.save_meta.timestamp,
        character_name=payload.character.name,
        character_level=payload.character.level,
        playtime_seconds=payload.character.playtime_seconds,
        currency_silver=payload.character.currency_silver,
        raw_data=raw,
        checksum=checksum,
    )
    db.add(snapshot)
    await db.flush()

    for item in payload.inventory:
        db.add(InventorySnapshot(
            snapshot_id=snapshot.id,
            item_key=item.item_key,
            item_name=item.name,
            stack_count=item.stack_count,
            slot_index=item.slot_index,
        ))

    for eq in payload.equipment:
        db.add(EquipmentSnapshot(
            snapshot_id=snapshot.id,
            item_key=eq.item_key,
            item_name=eq.name,
            enchant_level=eq.enchant_level,
            endurance=eq.endurance,
            sharpness=eq.sharpness,
            slot_type=eq.slot_type,
        ))

    for q in payload.quests:
        db.add(QuestSnapshot(
            snapshot_id=snapshot.id,
            quest_key=q.quest_key,
            quest_name=q.name,
            status=q.status,
            completed_at=q.completed_at,
        ))

    await db.commit()
    return {"status": "ok", "snapshot_id": snapshot.id}


@app.get("/api/snapshots", response_model=list[SnapshotSummary])
async def list_snapshots(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    since: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Snapshot).order_by(desc(Snapshot.uploaded_at))
    if since:
        q = q.where(Snapshot.uploaded_at >= since)
    q = q.offset(offset).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@app.get("/api/snapshots/{snapshot_id}", response_model=SnapshotDetail)
async def get_snapshot(snapshot_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Snapshot).where(Snapshot.id == snapshot_id))
    snap = result.scalar_one_or_none()
    if not snap:
        raise HTTPException(404, "Snapshot not found")
    return snap


@app.get("/api/latest", response_model=SnapshotDetail)
async def get_latest(db: AsyncSession = Depends(get_db)):
    snap = await _latest_snapshot(db)
    if not snap:
        raise HTTPException(404, "No snapshots yet")
    return snap


@app.get("/api/character", response_model=CharacterResponse)
async def get_character(db: AsyncSession = Depends(get_db)):
    snap = await _latest_snapshot(db)
    if not snap:
        raise HTTPException(404, "No snapshots yet")
    raw = snap.raw_data or {}
    stats = raw.get("character", {}).get("stats", {})
    return CharacterResponse(
        name=snap.character_name,
        level=snap.character_level,
        playtime_seconds=snap.playtime_seconds,
        currency_silver=snap.currency_silver,
        stats=stats,
        snapshot_id=snap.id,
        uploaded_at=snap.uploaded_at,
    )


@app.get("/api/inventory", response_model=list[InventoryItemResponse])
async def get_inventory(db: AsyncSession = Depends(get_db)):
    snap = await _latest_snapshot(db)
    if not snap:
        return []
    result = await db.execute(
        select(InventorySnapshot).where(InventorySnapshot.snapshot_id == snap.id)
    )
    items = result.scalars().all()
    raw_inv = (snap.raw_data or {}).get("inventory", [])
    cat_map = {i["item_key"]: i.get("category", "Unknown") for i in raw_inv}
    return [
        InventoryItemResponse(
            item_key=i.item_key,
            item_name=i.item_name,
            stack_count=i.stack_count,
            slot_index=i.slot_index,
            category=cat_map.get(i.item_key, "Unknown"),
        )
        for i in items
    ]


@app.get("/api/equipment", response_model=list[EquipmentItemResponse])
async def get_equipment(db: AsyncSession = Depends(get_db)):
    snap = await _latest_snapshot(db)
    if not snap:
        return []
    result = await db.execute(
        select(EquipmentSnapshot).where(EquipmentSnapshot.snapshot_id == snap.id)
    )
    return result.scalars().all()


@app.get("/api/quests", response_model=list[QuestResponse])
async def get_quests(db: AsyncSession = Depends(get_db)):
    snap = await _latest_snapshot(db)
    if not snap:
        return []
    result = await db.execute(
        select(QuestSnapshot).where(QuestSnapshot.snapshot_id == snap.id)
    )
    return result.scalars().all()


@app.get("/api/mercenaries", response_model=list[MercenaryResponse])
async def get_mercenaries(db: AsyncSession = Depends(get_db)):
    snap = await _latest_snapshot(db)
    if not snap:
        return []
    raw = (snap.raw_data or {}).get("mercenaries", [])
    return [MercenaryResponse(**m) for m in raw]


@app.get("/api/timeline", response_model=list[TimelinePoint])
async def get_timeline(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
):
    from datetime import timedelta

    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(Snapshot)
        .where(Snapshot.uploaded_at >= since)
        .order_by(Snapshot.uploaded_at)
    )
    snapshots = result.scalars().all()

    timeline = []
    for snap in snapshots:
        inv_count = await db.execute(
            select(func.count())
            .select_from(InventorySnapshot)
            .where(InventorySnapshot.snapshot_id == snap.id)
        )
        quest_count = await db.execute(
            select(func.count())
            .select_from(QuestSnapshot)
            .where(
                QuestSnapshot.snapshot_id == snap.id,
                QuestSnapshot.status == "completed",
            )
        )
        timeline.append(
            TimelinePoint(
                uploaded_at=snap.uploaded_at,
                character_level=snap.character_level,
                currency_silver=snap.currency_silver,
                playtime_seconds=snap.playtime_seconds,
                inventory_count=inv_count.scalar() or 0,
                quests_completed=quest_count.scalar() or 0,
            )
        )
    return timeline


@app.get("/api/items/search")
async def search_items(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Item).where(Item.name.ilike(f"%{q}%")).limit(50)
    )
    return [{"item_key": i.item_key, "name": i.name, "category": i.category} for i in result.scalars().all()]
