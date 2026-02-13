from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage for role requests
ROLE_REQUESTS_DB = []

class RoleRequestSchema(BaseModel):
    id: Optional[str] = None
    userId: str
    userName: str
    userEmail: str
    requestedRole: str
    timestamp: Optional[str] = None
    status: str = 'pending'

@router.get("/", response_model=List[RoleRequestSchema])
async def get_role_requests():
    return ROLE_REQUESTS_DB

@router.post("/", response_model=RoleRequestSchema)
async def create_role_request(req: RoleRequestSchema):
    new_req = req.model_copy()
    new_req.id = str(uuid.uuid4())
    new_req.timestamp = datetime.now().isoformat()
    ROLE_REQUESTS_DB.insert(0, new_req)
    return new_req

@router.put("/{request_id}/status")
async def update_role_request_status(request_id: str, status: str):
    for req in ROLE_REQUESTS_DB:
        if req.id == request_id:
            req.status = status
            return req
    raise HTTPException(status_code=404, detail="Role request not found")
