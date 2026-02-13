from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.middleware.tenant import get_current_tenant_id
from app.db.session import get_db
from app.services.reliability import reliability_service
from app.schemas.reliability import TelemetryIngest
from typing import Any

router = APIRouter()

@router.post("/ingest/{asset_id}")
async def ingest_telemetry(
    asset_id: str,
    data: TelemetryIngest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Primary endpoint for industrial telemetry streams.
    Enforces multi-tenancy and triggers the reliability engine.
    """
    try:
        result = await reliability_service.ingest_telemetry(
            db, tenant_id, asset_id, data.model_dump()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
