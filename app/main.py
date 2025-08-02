from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.requests import Request
from sqlalchemy.orm import Session
import os
from typing import Optional

from .database import SessionLocal, engine
from .models import Base
from .auth import authenticate_user, create_access_token, get_current_user
from .api.devices import router as devices_router
from .api.auth import router as auth_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Network Automation Platform", version="1.0.0")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional authentication for HTML pages (redirects to login)
async def get_current_user_optional(request: Request):
    """Get current user or redirect to login page for HTML routes"""
    try:
        # Check if we have a token in the Authorization header or in localStorage
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            # For HTML pages, redirect to login
            return None
        
        # Extract token from header
        token = auth_header.replace("Bearer ", "")
        from .auth import get_current_user
        # This is a simplified version - in practice you'd validate the token
        return {"email": "user@example.com"}  # Placeholder
    except:
        return None

# Mount static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(devices_router, prefix="/api", tags=["devices"])

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard/index.html", {"request": request, "user": {"email": "user@example.com"}})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard/index.html", {"request": request, "user": {"email": "user@example.com"}})

@app.get("/devices", response_class=HTMLResponse)
async def devices_page(request: Request):
    return templates.TemplateResponse("device/index.html", {"request": request, "user": {"email": "user@example.com"}})

@app.get("/automation", response_class=HTMLResponse)
async def automation_page(request: Request):
    return templates.TemplateResponse("automation/index.html", {"request": request, "user": {"email": "user@example.com"}})

@app.get("/operations", response_class=HTMLResponse)
async def operations_page(request: Request):
    return templates.TemplateResponse("operations/index.html", {"request": request, "user": {"email": "user@example.com"}})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("settings/index.html", {"request": request, "user": {"email": "user@example.com"}})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat/index.html", {"request": request, "user": {"email": "user@example.com"}})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    return response

# API endpoints for dashboard data
@app.get("/api/stats")
async def get_stats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    from .models.device import Device
    
    devices = db.query(Device).filter(Device.owner_id == current_user.id).all()
    total_devices = len(devices)
    online_devices = len([d for d in devices if d.status == 'online'])
    offline_devices = total_devices - online_devices
    online_percentage = int((online_devices / total_devices * 100) if total_devices > 0 else 0)
    
    return {
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": offline_devices,
            "online_percentage": online_percentage
        }
    }

@app.get("/api/device-status-chart")
async def get_device_status_chart(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    from .models.device import Device
    
    devices = db.query(Device).filter(Device.owner_id == current_user.id).all()
    online = len([d for d in devices if d.status == 'online'])
    offline = len([d for d in devices if d.status == 'offline'])
    warning = 0  # Placeholder
    
    return {
        "labels": ["Online", "Offline", "Warning"],
        "data": [online, offline, warning],
        "backgroundColor": ["#22c55e", "#ef4444", "#f59e0b"]
    }

@app.get("/api/operations-timeline")
async def get_operations_timeline(current_user: dict = Depends(get_current_user)):
    # Mock data for operations timeline
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "data": [12, 19, 3, 5, 2, 3]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
