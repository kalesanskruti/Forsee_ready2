from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic.networks import EmailStr

from app.api.v1.endpoints import login
from app.core import security
from app.db.session import get_db
from app.db.models import User, Tenant
from app.schemas import user as user_schema
import uuid

from app.api import deps

router = APIRouter()

@router.get("/me", response_model=user_schema.User)
async def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/role", response_model=user_schema.User)
async def update_user_role(
    *,
    db: AsyncSession = Depends(get_db),
    role: str = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update user role.
    """
    if role not in ["viewer", "engineer", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    current_user.role = role
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/", response_model=user_schema.User)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: user_schema.UserCreate,
) -> Any:
    """
    Create new user with a default tenant.
    """
    try:
        # 1. Check if user exists
        stmt = select(User).where(User.email == user_in.email)
        existing_user = await db.scalar(stmt)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )

        # 2. Create a new Tenant for the user (Self-Serve Signup)
        tenant_id = str(uuid.uuid4())
        org_name = f"{user_in.full_name or user_in.email}'s Org"
        
        tenant = Tenant(id=tenant_id, name=org_name, license_tier="free")
        db.add(tenant)
        
        # 3. Create User
        from loguru import logger
        logger.info(f"Received password length: {len(user_in.password)}")
        
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=security.get_password_hash(user_in.password),
            is_active=True,
            tenant_id=tenant_id
        )
        db.add(user)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    except Exception as e:
        from loguru import logger
        import traceback
        logger.error(f"Error creating user: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
