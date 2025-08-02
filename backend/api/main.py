from fastapi import APIRouter

# Import routers from different services
from backend.dashboard.routes import router as dashboard_router
from backend.devices.routes import router as devices_router
from backend.settings.routes import router as settings_router
from backend.users.routes import router as users_router
from backend.actions.routes import router as actions_router
from backend.operations.routes import router as operations_router
from backend.auth.routes import router as auth_router
from backend.api.v1.endpoints.genai import router as genai_router
from backend.automation.routes import router as automation_router
from backend.genai_settings.routes import router as genai_settings_router

# Create main API router
api_router = APIRouter()

# Include all service routers
api_router.include_router(auth_router, prefix="/v1/auth", tags=["authentication"])
api_router.include_router(dashboard_router, prefix="/v1/dashboard", tags=["dashboard"])
api_router.include_router(devices_router, prefix="/v1/devices", tags=["devices"])
api_router.include_router(settings_router, prefix="/v1/settings", tags=["settings"])
api_router.include_router(users_router, prefix="/v1/users", tags=["users"])
api_router.include_router(actions_router, prefix="/v1/actions", tags=["actions"])
api_router.include_router(operations_router, prefix="/v1/operations", tags=["operations"])
api_router.include_router(operations_router, prefix="/operations", tags=["operations-compat"])  # Frontend compatibility
api_router.include_router(genai_router, prefix="/v1/genai", tags=["genai"])
api_router.include_router(automation_router, prefix="/v1/automation", tags=["automation"])
api_router.include_router(genai_settings_router, prefix="/v1/genai-settings", tags=["genai-settings"])

# Dashboard API endpoints needed by frontend
@api_router.get("/stats") 
async def get_dashboard_stats():
    """Get dashboard statistics - used by frontend dashboard"""
    return {
        "devices": {
            "total": 15,
            "online": 12,
            "offline": 2,
            "warning": 1,
            "online_percentage": 80.0
        },
        "operations": {
            "total_today": 45,
            "successful": 42,
            "failed": 3,
            "success_rate": 93.3
        },
        "system": {
            "cpu_usage": 45.2,
            "memory_usage": 62.1,
            "disk_usage": 78.5
        }
    }

@api_router.get("/device-status-chart")
async def get_device_status_chart():
    """Get device status chart data"""
    return {
        "labels": ["Online", "Offline", "Warning"],
        "data": [12, 2, 1],
        "backgroundColor": ["#22c55e", "#ef4444", "#f59e0b"]
    }

@api_router.get("/operations-timeline")
async def get_operations_timeline():
    """Get operations timeline data"""
    from datetime import datetime, timedelta
    
    # Generate sample data for the last 7 days
    labels = []
    data = []
    
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        labels.append(date.strftime("%m/%d"))
        data.append(5 + (i * 2) + (i % 3))  # Sample data
    
    return {
        "labels": labels,
        "data": data
    }

@api_router.get("/network-operations/status")
def get_network_operations_status():
    return {"message": "Network operations service status", "status": "active"}

@api_router.get("/chat/status")
def get_chat_status():
    return {"message": "Chat service status", "status": "active"}
