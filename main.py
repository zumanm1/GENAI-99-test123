# DEVELOPMENT NOTE: 
# During development, DO NOT use Docker or Docker Compose!
# This main.py runs the FastAPI application directly using Python/uvicorn.
# ChromaDB and Ollama services should be started locally, not via Docker.
# Docker will be used only after successful development completion.

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
import uuid

# Import AI components
from backend.ai.llm_manager import llm_manager, LLMSettings

# Load environment variables from .env file
load_dotenv()

# Create the FastAPI app
app = FastAPI(
    title="Network Automation Application",
    description="A GENAI-powered network automation application for Cisco devices",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    """
    Initializes LLM providers on application startup.
    """
    print("Initializing LLM providers...")
    
    # Configure OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and openai_api_key != "your_openai_api_key":
        print("Found OpenAI API key. Configuring provider...")
        openai_settings = LLMSettings(provider="openai", api_key=openai_api_key, model="gpt-4")
        llm_manager.add_provider("openai", openai_settings)
    else:
        print("OpenAI API key not found or is a placeholder. Skipping.")

    # Configure Groq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and groq_api_key != "your_groq_api_key":
        print("Found Groq API key. Configuring provider...")
        groq_settings = LLMSettings(provider="groq", api_key=groq_api_key, model="llama3-70b-8192")
        llm_manager.add_provider("groq", groq_settings)
    else:
        print("Groq API key not found or is a placeholder. Skipping.")

    # Configure OpenRouter
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key and openrouter_api_key != "your_openrouter_api_key":
        print("Found OpenRouter API key. Configuring provider...")
        openrouter_settings = LLMSettings(provider="openrouter", api_key=openrouter_api_key, model="openai/gpt-4")
        llm_manager.add_provider("openrouter", openrouter_settings)
    else:
        print("OpenRouter API key not found or is a placeholder. Skipping.")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],  # Allow the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the main API router
from backend.api.main import api_router

# Setup static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Include the main API router
app.include_router(api_router, prefix="/api")

# Add WebSocket support for operations
from backend.websocket_manager import connection_manager
from fastapi import WebSocket, WebSocketDisconnect
import json

@app.websocket("/ws/operations")
async def websocket_operations(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    
    try:
        await connection_manager.connect(websocket, client_id, "command_execution")
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await connection_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": str(uuid.uuid4())  # Simple timestamp
                    }, client_id)
                elif message.get("type") == "subscribe":
                    operation_type = message.get("operation_type", "command_execution")
                    if operation_type in connection_manager.operation_connections:
                        connection_manager.operation_connections[operation_type].add(client_id)
                        await connection_manager.send_personal_message({
                            "type": "subscribed",
                            "operation_type": operation_type,
                            "message": f"Subscribed to {operation_type} updates"
                        }, client_id)
                        
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        connection_manager.disconnect(client_id)

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard/index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/devices", response_class=HTMLResponse)
async def devices(request: Request):
    return templates.TemplateResponse("devices/index.html", {"request": request})

@app.get("/automation", response_class=HTMLResponse)
async def automation(request: Request):
    return templates.TemplateResponse("automation/index.html", {"request": request})

@app.get("/operations", response_class=HTMLResponse)
async def operations(request: Request):
    return templates.TemplateResponse("operations/index.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return templates.TemplateResponse("settings/index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("chat/index.html", {"request": request})

@app.get("/genai-settings", response_class=HTMLResponse)
async def genai_settings(request: Request):
    return templates.TemplateResponse("genai-settings/index.html", {"request": request})

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """Handle 404 errors with custom page"""
    error_id = str(uuid.uuid4())[:8]
    return templates.TemplateResponse(
        "errors/404.html", 
        {"request": request, "error_id": error_id}, 
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors"""
    error_id = str(uuid.uuid4())[:8]
    return templates.TemplateResponse(
        "errors/500.html", 
        {"request": request, "error_id": error_id}, 
        status_code=500
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "network-automation-api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", 8002))  # Use FASTAPI_PORT from .env
    uvicorn.run(app, host="0.0.0.0", port=port)
