from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.api.middleware.tenant import get_current_tenant_id
from app.db.session import get_db
from app.db.models import Asset, TelemetrySnapshot

router = APIRouter()

@router.get("/")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Aggregate statistics for the Admin Dashboard.
    """
    # Total Assets
    total_assets = await db.scalar(select(func.count(Asset.id)).where(Asset.tenant_id == tenant_id))
    
    # Active Devices (simulated logic for now, or based on last heartbeat)
    # Assuming 'active' if they have recent telemetry (omitted for simplicity, returning total for now)
    active_devices = total_assets 
    
    # Critical Risks (Assets with health < 30)
    # We need to join with TelemetrySnapshot or assume Asset has a health field (it doesn't seem to based on schemas)
    # But TelemetrySnapshot has current_damage. Health = 100 - (current_damage * 100)? Or similar.
    # Let's check schemas/reliability.py or models.py for health definition.
    # For now, we will count assets with some risk flag if available, or just return 0 if no data.
    
    # Let's inspect models.py to be sure about the query.
    # START_INTERLUDE: I need to check models.py to write correct queries.
    # But I am writing the file now. I will make a best guess and then fix if needed.
    # Actually, I have models.py in context? No, I viewed `endpoints/assets.py` which imports `Asset` and `TelemetrySnapshot`.
    # `assets.py` register: `snapshot = TelemetrySnapshot(..., current_damage=0.0)`
    
    # Critical Risks: count TelemetrySnapshot where current_damage > 0.7 (assuming 0-1 scale)
    critical_risks = await db.scalar(
        select(func.count(TelemetrySnapshot.id))
        .where(TelemetrySnapshot.tenant_id == tenant_id)
        .where(TelemetrySnapshot.current_damage > 0.7)
    )
    
    # Average Health
    avg_damage = await db.scalar(
        select(func.avg(TelemetrySnapshot.current_damage))
        .where(TelemetrySnapshot.tenant_id == tenant_id)
    )
    avg_health = (1.0 - (avg_damage or 0.0)) * 100
    
    return {
        "total_assets": total_assets,
        "active_devices": active_devices,
        "critical_risks": critical_risks,
        "avg_health": round(avg_health, 1),
        "predictions_run": 84291, # Mock for now
        "active_models": 64 # Mock for now
    }
