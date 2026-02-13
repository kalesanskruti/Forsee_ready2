from typing import Optional
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_current_tenant_id(token: str = Depends(reusable_oauth2)) -> str:
    # ... previous logic ...
    return payload.get("tenant_id") # Simplified for readability in this chunk

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, token: str = Depends(reusable_oauth2)):
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_role = payload.get("role", "viewer")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return True

# Middleware to inject tenant filters automatically could be added here
# using contextvars for deeper DB integration if needed.
