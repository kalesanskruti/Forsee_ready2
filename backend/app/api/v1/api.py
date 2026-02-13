from fastapi import APIRouter
from app.api.v1.endpoints import login, reliability, assets, tenants, dashboard, system_requests, role_requests, users, chatbot

api_router = APIRouter()

api_router.include_router(login.router, tags=["Auth"])
api_router.include_router(reliability.router, prefix="/reliability", tags=["Reliability"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(system_requests.router, prefix="/system-requests", tags=["System Requests"])
api_router.include_router(role_requests.router, prefix="/role-requests", tags=["Role Requests"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])

@api_router.get("/info", tags=["System"])
async def get_system_info():
    return {"module": "FORSEE Intelligence Core", "status": "operational"}
