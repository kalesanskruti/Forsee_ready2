from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.middleware.tenant import RoleChecker
from app.db.session import get_db
from app.db.models import Tenant
from pydantic import BaseModel
from typing import List

router = APIRouter()
is_admin = RoleChecker(["admin"])

class TenantCreate(BaseModel):
    id: str
    name: str
    license_tier: str = "standard"

class TenantOut(BaseModel):
    id: str
    name: str
    license_tier: str

@router.post("/", response_model=TenantOut, dependencies=[Depends(is_admin)])
async def create_tenant(
    tenant_in: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new tenant. Restricted to Super Admins.
    """
    stmt = select(Tenant).where(Tenant.id == tenant_in.id)
    existing = await db.scalar(stmt)
    if existing:
        raise HTTPException(status_code=400, detail="Tenant ID already exists")
    
    tenant = Tenant(**tenant_in.model_dump())
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant

@router.get("/", response_model=List[TenantOut], dependencies=[Depends(is_admin)])
async def list_tenants(db: AsyncSession = Depends(get_db)):
    """
    List all tenants.
    """
    stmt = select(Tenant)
    result = await db.scalars(stmt)
    return result
