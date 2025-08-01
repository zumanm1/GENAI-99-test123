from fastapi import APIRouter

# Import routers from different services
from backend.dashboard.routes import router as dashboard_router
from backend.devices.routes import router as devices_router
from backend.settings.routes import router as settings_router
from backend.users.routes import router as users_router
from backend.actions.routes import router as actions_router
from backend.api.v1.endpoints.genai import router as genai_router

# Create main API router
api_router = APIRouter()

# Include all service routers
api_router.include_router(dashboard_router, prefix="/v1/dashboard", tags=["dashboard"])
api_router.include_router(devices_router, prefix="/v1/devices", tags=["devices"])
api_router.include_router(settings_router, prefix="/v1/settings", tags=["settings"])
api_router.include_router(users_router, prefix="/v1/users", tags=["users"])
api_router.include_router(actions_router, prefix="/v1/actions", tags=["actions"])
api_router.include_router(genai_router, prefix="/v1/genai", tags=["genai"])


@api_router.get("/network-operations/status")
def get_network_operations_status():
    return {"message": "Network operations service status", "status": "active"}

@api_router.get("/chat/status")
def get_chat_status():
    return {"message": "Chat service status", "status": "active"}