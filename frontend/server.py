from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocketDisconnect
import os

# Initialize the FastAPI app
app = FastAPI(
    title="Network Automation Frontend",
    description="Frontend server for serving static files and real-time updates",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templating
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home():
    return HTMLResponse("Hello World! This is the frontend server.")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        pass

@app.get("/dashboard")
async def get_dashboard(request):
    """Dashboard page rendering"""
    return templates.TemplateResponse("dashboard/index.html", {"request": request})

@app.get("/device-management")
async def get_device_management(request):
    """Device management page"""
    return templates.TemplateResponse("device/index.html", {"request": request})

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files directory
static_files_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_files_path), name="static")

# Path to the frontend directory
frontend_dir = os.path.dirname(__file__)

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_dir, 'index.html'))

@app.get("/devices")
async def read_devices():
    return FileResponse(os.path.join(frontend_dir, 'devices.html'))

@app.get("/genai")
async def read_genai():
    return FileResponse(os.path.join(frontend_dir, 'genai.html'))

if __name__ == "__main__":
    # Run the server using FRONTEND_PORT from .env, default to 8001
    port = int(os.getenv("FRONTEND_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
