from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DeviceBase(BaseModel):
    """
    Base schema for device information
    """
    name: str = Field(..., example="Router R15")
    ip_address: str = Field(..., example="192.168.1.15")
    device_type: str = Field(..., example="ios", description="Device type: ios, iosxr, iosxe")
    username: str = Field(..., example="admin")
    port: int = Field(22, example=22, description="SSH/Telnet port")
    protocol: str = Field("ssh", example="ssh", description="Connection protocol: ssh, telnet")

class DeviceCreate(DeviceBase):
    """
    Schema for creating a new device
    """
    password: str = Field(..., example="password123", description="Device password")

class DeviceUpdate(BaseModel):
    """
    Schema for updating device information
    """
    name: Optional[str] = Field(None, example="Router R15")
    ip_address: Optional[str] = Field(None, example="192.168.1.15")
    device_type: Optional[str] = Field(None, example="ios")
    username: Optional[str] = Field(None, example="admin")
    password: Optional[str] = Field(None, example="newpassword123")
    port: Optional[int] = Field(None, example=22)
    protocol: Optional[str] = Field(None, example="ssh")

class DeviceInDBBase(DeviceBase):
    """
    Base schema for device information in database
    """
    id: int
    status: str = "unknown"
    last_polled: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Device(DeviceInDBBase):
    """
    Schema for device information returned to client
    """
    pass

class DeviceInDB(DeviceInDBBase):
    """
    Schema for device information in database with hashed password
    """
    hashed_password: str

class DeviceTestConnection(BaseModel):
    """
    Schema for testing device connection
    """
    ip_address: str = Field(..., example="192.168.1.15")
    username: str = Field(..., example="admin")
    password: str = Field(..., example="password123")
    port: int = Field(22, example=22)
    protocol: str = Field("ssh", example="ssh")

class DevicePingResult(BaseModel):
    """
    Schema for device ping test result
    """
    ip_address: str = Field(..., example="192.168.1.15")
    reachable: bool
    response_time: Optional[float] = None
    message: str

class DevicePollResult(BaseModel):
    """
    Schema for device polling result
    """
    device_id: int
    status: str
    message: str
    timestamp: datetime

class DevicesPollResult(BaseModel):
    """
    Schema for polling multiple devices
    """
    total_devices: int
    successful_polls: int
    failed_polls: int
    results: List[DevicePollResult]

class DeviceStatusUpdate(BaseModel):
    """
    Schema for updating device status
    """
    status: str = Field(..., example="online", description="Device status: online, offline, error")