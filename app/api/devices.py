from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
import ipaddress

from ..database import get_db
from ..auth import get_current_user
from ..models.device import Device
from ..models.user import User

router = APIRouter()

# Pydantic models for request/response
class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Device name cannot be empty")
    ip_address: str = Field(..., description="Valid IP address required")
    model: str = Field(..., min_length=1, description="Device model cannot be empty")
    status: str = "offline"
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError('Invalid IP address format')

from datetime import datetime

class DeviceResponse(BaseModel):
    id: int
    name: str
    ip_address: str
    model: str
    status: str
    last_seen: datetime
    
    class Config:
        from_attributes = True

@router.get("/devices", response_model=List[DeviceResponse])
async def get_devices(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    devices = db.query(Device).filter(Device.owner_id == current_user.id).all()
    return devices

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = Device(**device.dict(), owner_id=current_user.id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.owner_id == current_user.id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.put("/devices/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: int, device: DeviceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.id == device_id, Device.owner_id == current_user.id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    
    for key, value in device.dict().items():
        setattr(db_device, key, value)
    
    db.commit()
    db.refresh(db_device)
    return db_device

@router.delete("/devices/{device_id}")
async def delete_device(device_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.id == device_id, Device.owner_id == current_user.id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(db_device)
    db.commit()
    return {"detail": "Device deleted successfully"}
