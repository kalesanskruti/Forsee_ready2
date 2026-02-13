from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.db.models import User
from app.schemas.token import Token

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, retrieve a JWT token
    """
    stmt = select(User).where(User.email == form_data.username)
    user = await db.scalar(stmt)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, tenant_id=user.tenant_id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel

class GoogleToken(BaseModel):
    id_token: str

import requests

@router.post("/login/google", response_model=Token)
async def login_google(
    token_data: GoogleToken,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Verify Google access token and return a JWT access token
    """
    try:
        # Fetch user info from Google using the access token
        user_info_res = requests.get(
            f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token_data.id_token}"
        )
        
        if user_info_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google token")
            
        idinfo = user_info_res.json()
        email = idinfo['email']
        full_name = idinfo.get('name', '')
        
        # Check/Create user
        stmt = select(User).where(User.email == email)
        user = await db.scalar(stmt)
        
        if not user:
            # 1. Create a new Tenant for the Google user
            import uuid
            from app.db.models import Tenant
            
            tenant_id = str(uuid.uuid4())
            org_name = f"{full_name or email}'s Org"
            
            tenant = Tenant(id=tenant_id, name=org_name, license_tier="free")
            db.add(tenant)
            await db.flush() # Ensure tenant is inserted before user

            # 2. Auto-register Google user
            user = User(
                email=email,
                full_name=full_name,
                hashed_password="google-auth-no-password", # Dummy
                is_active=True,
                tenant_id=tenant_id
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                user.id, tenant_id=user.tenant_id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    except Exception as e:
        print(f"Google Login Error: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error during Google login")
