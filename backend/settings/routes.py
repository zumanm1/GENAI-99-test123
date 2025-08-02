from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.connection import get_db
from ..database.models import LLMSetting, APIKey
from ..utils.logger import log_api_request
from ..utils.exceptions import DatabaseException

router = APIRouter()

@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    """Get application settings overview"""
    try:
        llm_setting = db.query(LLMSetting).filter(LLMSetting.is_active == True).first()
        api_keys_count = db.query(APIKey).filter(APIKey.is_active == True).count()
        
        log_api_request("GET", "/settings/", status.HTTP_200_OK)
        return {
            "message": "Application settings",
            "llm_provider": llm_setting.provider if llm_setting else "openai",
            "model": llm_setting.model if llm_setting else "gpt-3.5-turbo",
            "api_keys_configured": api_keys_count
        }
    except Exception as e:
        log_api_request("GET", "/settings/", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/settings/genai/llm")
def get_llm_settings(db: Session = Depends(get_db)):
    """Get current LLM settings"""
    try:
        llm_setting = db.query(LLMSetting).filter(LLMSetting.is_active == True).first()
        
        if not llm_setting:
            log_api_request("GET", "/settings/llm", status.HTTP_404_NOT_FOUND)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active LLM settings found")
        
        log_api_request("GET", "/settings/llm", status.HTTP_200_OK)
        return {
            "id": llm_setting.id,
            "provider": llm_setting.provider,
            "model": llm_setting.model,
            "temperature": llm_setting.temperature,
            "max_tokens": llm_setting.max_tokens,
            "is_active": llm_setting.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        log_api_request("GET", "/settings/llm", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/llm")
def update_llm_settings(provider: str, model: str, temperature: float = 0.7, max_tokens: int = 2000, db: Session = Depends(get_db)):
    """Update LLM settings"""
    try:
        # Deactivate current active setting
        db.query(LLMSetting).filter(LLMSetting.is_active == True).update({"is_active": False})
        
        # Create new active setting
        new_setting = LLMSetting(
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            is_active=True
        )
        db.add(new_setting)
        db.commit()
        db.refresh(new_setting)
        
        log_api_request("PUT", "/settings/llm", status.HTTP_200_OK)
        return {
            "message": "LLM settings updated successfully",
            "id": new_setting.id,
            "provider": new_setting.provider,
            "model": new_setting.model
        }
    except Exception as e:
        db.rollback()
        log_api_request("PUT", "/settings/llm", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/api-keys")
def get_api_keys(db: Session = Depends(get_db)):
    """Get all API keys (without exposing actual key values)"""
    try:
        api_keys = db.query(APIKey).filter(APIKey.is_active == True).all()
        
        keys_data = []
        for key in api_keys:
            keys_data.append({
                "id": key.id,
                "name": key.name,
                "service": key.service,
                "is_active": key.is_active,
                "created_at": key.created_at.isoformat() if key.created_at else None
            })
        
        log_api_request("GET", "/settings/api-keys", status.HTTP_200_OK)
        return {"keys": keys_data}
    except Exception as e:
        log_api_request("GET", "/settings/api-keys", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/api-keys")
def add_api_key(name: str, service: str, key: str, db: Session = Depends(get_db)):
    """Add a new API key"""
    try:
        # Check if key with same name already exists
        existing_key = db.query(APIKey).filter(APIKey.name == name, APIKey.is_active == True).first()
        if existing_key:
            log_api_request("POST", "/settings/api-keys", status.HTTP_400_BAD_REQUEST)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="API key with this name already exists")
        
        # Create new API key (in production, encrypt the key)
        new_key = APIKey(
            name=name,
            service=service,
            key=key,  # TODO: Encrypt this in production
            is_active=True
        )
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        
        log_api_request("POST", "/settings/api-keys", status.HTTP_201_CREATED)
        return {
            "message": "API key added successfully",
            "id": new_key.id,
            "name": new_key.name,
            "service": new_key.service
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_api_request("POST", "/settings/api-keys", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/api-keys/{key_id}")
def update_api_key(key_id: int, name: str = None, service: str = None, key: str = None, db: Session = Depends(get_db)):
    """Update an existing API key"""
    try:
        api_key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.is_active == True).first()
        if not api_key:
            log_api_request("PUT", f"/settings/api-keys/{key_id}", status.HTTP_404_NOT_FOUND)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
        
        # Update fields if provided
        if name is not None:
            api_key.name = name
        if service is not None:
            api_key.service = service
        if key is not None:
            api_key.key = key  # TODO: Encrypt this in production
        
        db.commit()
        db.refresh(api_key)
        
        log_api_request("PUT", f"/settings/api-keys/{key_id}", status.HTTP_200_OK)
        return {
            "message": f"API key {key_id} updated successfully",
            "id": api_key.id,
            "name": api_key.name,
            "service": api_key.service
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_api_request("PUT", f"/settings/api-keys/{key_id}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/api-keys/{key_id}")
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an API key (soft delete by setting is_active to False)"""
    try:
        api_key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.is_active == True).first()
        if not api_key:
            log_api_request("DELETE", f"/settings/api-keys/{key_id}", status.HTTP_404_NOT_FOUND)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
        
        # Soft delete by setting is_active to False
        api_key.is_active = False
        db.commit()
        
        log_api_request("DELETE", f"/settings/api-keys/{key_id}", status.HTTP_200_OK)
        return {"message": f"API key {key_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_api_request("DELETE", f"/settings/api-keys/{key_id}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))