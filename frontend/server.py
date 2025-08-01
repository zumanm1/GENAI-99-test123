import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

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
    # Run the server on port 8001, accessible from anywhere
    uvicorn.run(app, host="0.0.0.0", port=8001)
