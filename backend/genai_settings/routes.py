from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json
import os
import logging

from ..database.database import get_db
from ..database.models import SystemConfig, User
from ..utils.logger import log_api_request

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for GenAI Settings
class LLMSettingsRequest(BaseModel):
    primary_llm: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    fallback_llm: str
    retry_attempts: int = 3
    timeout_settings: int = 120
    specialized_models: Dict[str, str] = {}

class RAGSettingsRequest(BaseModel):
    cisco_documentation_enabled: bool = True
    cisco_doc_version: str = "Latest"
    update_frequency: str = "Weekly"
    similarity_threshold: float = 0.7
    max_retrieved_chunks: int = 5
    chunk_size: int = 1024
    overlap_percentage: int = 20

class AgenticSettingsRequest(BaseModel):
    planning_agent_enabled: bool = True
    reasoning_depth: str = "Intermediate"
    step_validation: bool = True
    execution_agent_enabled: bool = True
    auto_execution_enabled: bool = False
    safety_checks: str = "Syntax + Logic"
    rollback_capability: bool = True
    multi_agent_workflow: bool = True
    conflict_resolution: str = "Human intervention"
    feedback_loop: bool = True

class GraphRAGSettingsRequest(BaseModel):
    knowledge_graph_enabled: bool = False
    entity_extraction_enabled: bool = True
    configuration_relationships: bool = True
    topology_connections: bool = True
    graph_provider: str = "Neo4j"
    connection_string: str = ""
    indexing_strategy: str = "Batch"
    dynamic_graph_updates: bool = False
    agent_graph_reasoning: bool = False

class EmbeddingsSettingsRequest(BaseModel):
    text_embeddings_model: str = "text-embedding-ada-002"
    dimensions: int = 1536
    batch_size: int = 64
    config_embeddings_enabled: bool = True
    network_topology_embeddings: bool = False
    vector_database_provider: str = "Chroma"
    index_type: str = "HNSW"
    distance_metric: str = "Cosine"

class APIKeyRequest(BaseModel):
    name: str
    service: str
    key: str
    organization_id: Optional[str] = None

class CoreSettingsRequest(BaseModel):
    default_chat_provider: str = "openai"
    default_config_generation_provider: str = "openai"
    default_analysis_provider: str = "openai"
    response_timeout: int = 120
    concurrent_requests: int = 5
    cache_enabled: bool = True
    cache_duration: int = 3600
    cache_size_limit: int = 1024
    max_devices_per_operation: int = 10
    require_approval_threshold: str = "10+ devices"
    safety_validation_level: str = "Standard"
    log_all_operations: bool = True

# LLM Settings endpoints
@router.get("/genai/llm")
async def get_llm_settings(db: Session = Depends(get_db)):
    """Get current LLM settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "llm_settings").first()
        if not config:
            # Return defaults
            return {
                "primary_llm": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 1.0,
                "fallback_llm": "gpt-3.5-turbo",
                "retry_attempts": 3,
                "timeout_settings": 120,
                "specialized_models": {
                    "network_config_llm": "gpt-4",
                    "troubleshooting_llm": "gpt-4",
                    "security_analysis_llm": "gpt-4"
                }
            }
        
        return config.config_value
    except Exception as e:
        logger.error(f"Error getting LLM settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/genai/llm")
async def update_llm_settings(
    settings: LLMSettingsRequest,
    db: Session = Depends(get_db)
):
    """Update LLM settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "llm_settings").first()
        
        if not config:
            config = SystemConfig(
                config_key="llm_settings",
                config_value=settings.dict(),
                description="LLM configuration settings"
            )
            db.add(config)
        else:
            config.config_value = settings.dict()
        
        db.commit()
        return {"message": "LLM settings updated successfully", "settings": settings.dict()}
    except Exception as e:
        logger.error(f"Error updating LLM settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# RAG Settings endpoints
@router.get("/genai/rag")
async def get_rag_settings(db: Session = Depends(get_db)):
    """Get current RAG settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "rag_settings").first()
        if not config:
            return {
                "cisco_documentation_enabled": True,
                "cisco_doc_version": "Latest",
                "update_frequency": "Weekly",
                "similarity_threshold": 0.7,
                "max_retrieved_chunks": 5,
                "chunk_size": 1024,
                "overlap_percentage": 20
            }
        
        return config.config_value
    except Exception as e:
        logger.error(f"Error getting RAG settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/genai/rag")
async def update_rag_settings(
    settings: RAGSettingsRequest,
    db: Session = Depends(get_db)
):
    """Update RAG settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "rag_settings").first()
        
        if not config:
            config = SystemConfig(
                config_key="rag_settings",
                config_value=settings.dict(),
                description="RAG configuration settings"
            )
            db.add(config)
        else:
            config.config_value = settings.dict()
        
        db.commit()
        return {"message": "RAG settings updated successfully", "settings": settings.dict()}
    except Exception as e:
        logger.error(f"Error updating RAG settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Agentic Settings endpoints
@router.get("/genai/agentic")
async def get_agentic_settings(db: Session = Depends(get_db)):
    """Get current Agentic settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "agentic_settings").first()
        if not config:
            return {
                "planning_agent_enabled": True,
                "reasoning_depth": "Intermediate",
                "step_validation": True,
                "execution_agent_enabled": True,
                "auto_execution_enabled": False,
                "safety_checks": "Syntax + Logic",
                "rollback_capability": True,
                "multi_agent_workflow": True,
                "conflict_resolution": "Human intervention",
                "feedback_loop": True
            }
        
        return config.config_value
    except Exception as e:
        logger.error(f"Error getting Agentic settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/genai/agentic")
async def update_agentic_settings(
    settings: AgenticSettingsRequest,
    db: Session = Depends(get_db)
):
    """Update Agentic settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "agentic_settings").first()
        
        if not config:
            config = SystemConfig(
                config_key="agentic_settings",
                config_value=settings.dict(),
                description="Agentic AI configuration settings"
            )
            db.add(config)
        else:
            config.config_value = settings.dict()
        
        db.commit()
        return {"message": "Agentic settings updated successfully", "settings": settings.dict()}
    except Exception as e:
        logger.error(f"Error updating Agentic settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Graph RAG Settings endpoints
@router.get("/genai/graph-rag")
async def get_graph_rag_settings(db: Session = Depends(get_db)):
    """Get current Graph RAG settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "graph_rag_settings").first()
        if not config:
            return {
                "knowledge_graph_enabled": False,
                "entity_extraction_enabled": True,
                "configuration_relationships": True,
                "topology_connections": True,
                "graph_provider": "Neo4j",
                "connection_string": "",
                "indexing_strategy": "Batch",
                "dynamic_graph_updates": False,
                "agent_graph_reasoning": False
            }
        
        return config.config_value
    except Exception as e:
        logger.error(f"Error getting Graph RAG settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/genai/graph-rag")
async def update_graph_rag_settings(
    settings: GraphRAGSettingsRequest,
    db: Session = Depends(get_db)
):
    """Update Graph RAG settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "graph_rag_settings").first()
        
        if not config:
            config = SystemConfig(
                config_key="graph_rag_settings",
                config_value=settings.dict(),
                description="Graph RAG configuration settings"
            )
            db.add(config)
        else:
            config.config_value = settings.dict()
        
        db.commit()
        return {"message": "Graph RAG settings updated successfully", "settings": settings.dict()}
    except Exception as e:
        logger.error(f"Error updating Graph RAG settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Embeddings Settings endpoints
@router.get("/genai/embeddings")
async def get_embeddings_settings(db: Session = Depends(get_db)):
    """Get current Embeddings settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "embeddings_settings").first()
        if not config:
            return {
                "text_embeddings_model": "text-embedding-ada-002",
                "dimensions": 1536,
                "batch_size": 64,
                "config_embeddings_enabled": True,
                "network_topology_embeddings": False,
                "vector_database_provider": "Chroma",
                "index_type": "HNSW",
                "distance_metric": "Cosine"
            }
        
        return config.config_value
    except Exception as e:
        logger.error(f"Error getting Embeddings settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/genai/embeddings")
async def update_embeddings_settings(
    settings: EmbeddingsSettingsRequest,
    db: Session = Depends(get_db)
):
    """Update Embeddings settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "embeddings_settings").first()
        
        if not config:
            config = SystemConfig(
                config_key="embeddings_settings",
                config_value=settings.dict(),
                description="Embeddings configuration settings"
            )
            db.add(config)
        else:
            config.config_value = settings.dict()
        
        db.commit()
        return {"message": "Embeddings settings updated successfully", "settings": settings.dict()}
    except Exception as e:
        logger.error(f"Error updating Embeddings settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# API Keys management
@router.get("/genai/api-keys")
async def get_api_keys(db: Session = Depends(get_db)):
    """Get all configured API keys (masked for security)"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "api_keys").first()
        if not config:
            return {"keys": []}
        
        # Mask the keys for security
        keys = config.config_value.get("keys", [])
        masked_keys = []
        for key in keys:
            masked_key = key.copy()
            if "key" in masked_key:
                masked_key["key"] = f"{'*' * 20}{masked_key['key'][-4:]}" if len(masked_key["key"]) > 4 else "****"
            masked_keys.append(masked_key)
        
        return {"keys": masked_keys}
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/genai/api-keys")
async def add_api_key(
    key_request: APIKeyRequest,
    db: Session = Depends(get_db)
):
    """Add a new API key"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "api_keys").first()
        
        if not config:
            keys_data = {"keys": []}
            config = SystemConfig(
                config_key="api_keys",
                config_value=keys_data,
                description="API keys configuration",
                is_encrypted=True
            )
            db.add(config)
        else:
            keys_data = config.config_value
        
        # Add new key
        new_key = {
            "id": len(keys_data["keys"]) + 1,
            "name": key_request.name,
            "service": key_request.service,
            "key": key_request.key,  # In production, this should be encrypted
            "organization_id": key_request.organization_id,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        keys_data["keys"].append(new_key)
        config.config_value = keys_data
        
        db.commit()
        
        return {"message": f"API key '{key_request.name}' added successfully", "id": new_key["id"]}
    except Exception as e:
        logger.error(f"Error adding API key: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/genai/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "api_keys").first()
        if not config:
            raise HTTPException(status_code=404, detail="No API keys found")
        
        keys_data = config.config_value
        keys = keys_data.get("keys", [])
        
        # Find and remove key
        keys_data["keys"] = [k for k in keys if k.get("id") != key_id]
        
        if len(keys_data["keys"]) == len(keys):
            raise HTTPException(status_code=404, detail="API key not found")
        
        config.config_value = keys_data
        db.commit()
        
        return {"message": f"API key {key_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Core Settings endpoints
@router.get("/genai/core")
async def get_core_settings(db: Session = Depends(get_db)):
    """Get current Core settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "core_settings").first()
        if not config:
            return {
                "default_chat_provider": "openai",
                "default_config_generation_provider": "openai",
                "default_analysis_provider": "openai",
                "response_timeout": 120,
                "concurrent_requests": 5,
                "cache_enabled": True,
                "cache_duration": 3600,
                "cache_size_limit": 1024,
                "max_devices_per_operation": 10,
                "require_approval_threshold": "10+ devices",
                "safety_validation_level": "Standard",
                "log_all_operations": True
            }
        
        return config.config_value
    except Exception as e:
        logger.error(f"Error getting Core settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/genai/core")
async def update_core_settings(
    settings: CoreSettingsRequest,
    db: Session = Depends(get_db)
):
    """Update Core settings"""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "core_settings").first()
        
        if not config:
            config = SystemConfig(
                config_key="core_settings",
                config_value=settings.dict(),
                description="Core system configuration settings"
            )
            db.add(config)
        else:
            config.config_value = settings.dict()
        
        db.commit()
        return {"message": "Core settings updated successfully", "settings": settings.dict()}
    except Exception as e:
        logger.error(f"Error updating Core settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Test API connection endpoint
@router.post("/genai/test-connection")
async def test_api_connection(
    provider: str,
    api_key: str
):
    """Test API connection for a provider"""
    try:
        if provider.lower() == "openai":
            import openai
            client = openai.OpenAI(api_key=api_key)
            # Test with a simple request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=5
            )
            return {"status": "success", "message": "OpenAI connection successful"}
        elif provider.lower() == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            # Test with a simple request
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Test"}]
            )
            return {"status": "success", "message": "Anthropic connection successful"}
        else:
            return {"status": "error", "message": f"Provider {provider} not supported"}
    except Exception as e:
        logger.error(f"API connection test failed: {e}")
        return {"status": "error", "message": str(e)}
