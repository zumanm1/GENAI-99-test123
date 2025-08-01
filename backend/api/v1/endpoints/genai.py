from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import time
from fastapi import APIRouter
from pydantic import BaseModel

# from backend.ai.crew import NetworkAutomationCrew
# from backend.ai.llm_manager import llm_manager

router = APIRouter()

class GenerateConfigRequest(BaseModel):
    requirements: str
    device_type: str

@router.post("/config/generate")
def generate_config(request: GenerateConfigRequest):
    """
    Generates and validates a network configuration using the AI crew.
    """
    try:
        # Initialize the crew
        network_crew = NetworkAutomationCrew(device_type=request.device_type)
        
        # Kick off the task
        result = network_crew.kickoff(requirements=request.requirements)
        
        return {"result": result}
    except Exception as e:
        # Log the exception for debugging
        print(f"Error generating config: {e}")
        # Return a user-friendly error message
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the configuration: {str(e)}"
        )
