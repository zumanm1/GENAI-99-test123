import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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

# Include the main API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Network Automation Application"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "network-automation-api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))  # Use port 8002 instead
    uvicorn.run(app, host="0.0.0.0", port=port)