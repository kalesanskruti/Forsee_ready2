from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.engines.shift import ShiftEngine
from app.engines.damage import DamageEngine
from app.engines.rul import RULEngine
from app.engines.environmental import EnvironmentalEngine
from app.core.bus import bus
from app.db.models import TelemetrySnapshot, Asset, AuditLog
from redis import Redis
from app.core.config import settings
from sqlalchemy import select, update
from loguru import logger

class ReliabilityService:
    def __init__(self):
        self.shift_engine = ShiftEngine()
        self.damage_engine = DamageEngine()
        self.rul_engine = RULEngine()
        self.env_engine = EnvironmentalEngine()
        self.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

    async def ingest_telemetry(self, db: AsyncSession, tenant_id: str, asset_id: str, telemetry: Dict[str, Any]):
        """
        Orchestrates the reliability pipeline:
        1. Context fetching
        2. Shift Violation check
        3. Environmental aging adjustment
        4. Damage Accumulation
        5. RUL Calculation
        6. State Update (DB + Redis)
        7. Event Emission (Kafka)
        """
        # 1. Fetch Asset and Config (Simplified for demo, usually from Redis/DB Cache)
        # config = await db.scalar(select(ShiftConfig).where(Asset.id == asset_id))
        shift_config = {"threshold_load": 80.0, "penalty_weight": 0.4} # Mocked config
        
        # 2. Shift check
        multiplier = await self.shift_engine.process(telemetry, shift_config)
        
        # 3. Env check
        env_modifier = await self.env_engine.process(telemetry)
        total_multiplier = multiplier * env_modifier
        
        # 4. Damage Accumulation
        # Current state
        stmt = select(TelemetrySnapshot).where(TelemetrySnapshot.asset_id == asset_id)
        snapshot = await db.scalar(stmt)
        if not snapshot:
            snapshot = TelemetrySnapshot(asset_id=asset_id, tenant_id=tenant_id, current_damage=0.0)
            db.add(snapshot)
            
        damage_increment = await self.damage_engine.process(telemetry, total_multiplier)
        new_damage = snapshot.current_damage + damage_increment
        
        # 5. RUL Calculation (using recent rate)
        # Assuming telemetry includes a timestamp-based rate or we calculate it here
        damage_rate = damage_increment # Simplistic delta-per-unit
        rul_data = await self.rul_engine.process(new_damage, damage_rate)
        
        # 6. Update State
        snapshot.current_damage = new_damage
        snapshot.current_load = telemetry.get("load", 0.0)
        snapshot.current_temp = telemetry.get("temp", 0.0)
        snapshot.current_rul = rul_data["rul"]
        snapshot.confidence_score = rul_data["confidence"]
        snapshot.last_update = telemetry
        
        # 7. Audit Log
        audit = AuditLog(
            tenant_id=tenant_id,
            entity_type="AssetRel",
            entity_id=asset_id,
            action="telemetry_processed",
            new_value={"damage": new_damage, "rul": rul_data["rul"]},
            metadata_info={"multiplier": total_multiplier}
        )
        db.add(audit)
        
        await db.commit()
        
        # 8. Update Redis Cache (Performance layer)
        redis_key = f"tenant:{tenant_id}:asset:{asset_id}:state"
        self.redis.hset(redis_key, mapping={
            "damage": str(new_damage),
            "rul": str(rul_data["rul"]),
            "confidence": str(rul_data["confidence"]),
            "timestamp": str(time.time())
        })
        
        # 9. Emit Events
        bus.emit("damage.updated", key=asset_id, data={"tenant_id": tenant_id, "damage": new_damage})
        bus.emit("rul.recalculated", key=asset_id, data={"tenant_id": tenant_id, "rul": rul_data["rul"]})
        
        return snapshot

reliability_service = ReliabilityService()
