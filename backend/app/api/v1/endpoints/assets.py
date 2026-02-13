from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.middleware.tenant import get_current_tenant_id, RoleChecker
from app.db.session import get_db
from app.db.models import Asset, TelemetrySnapshot
from typing import List

router = APIRouter()
is_engineer = RoleChecker(["admin", "engineer"])

@router.get("/", response_model=List[dict])
async def list_assets(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    List all assets for the current tenant.
    """
    stmt = select(Asset).where(Asset.tenant_id == tenant_id)
    result = await db.scalars(stmt)
    return [asset.__dict__ for asset in result]

@router.post("/register", dependencies=[Depends(is_engineer)])
async def register_asset(
    name: str,
    asset_type: str,
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Register a new industrial asset. Restricted to Engineers/Admins.
    """
    asset = Asset(id=asset_id, name=name, type=asset_type, tenant_id=tenant_id)
    db.add(asset)
    # Initialize health snapshot
    snapshot = TelemetrySnapshot(asset_id=asset_id, tenant_id=tenant_id, current_damage=0.0)
    db.add(snapshot)
    await db.commit()
    return {"status": "success", "asset_id": asset_id}
