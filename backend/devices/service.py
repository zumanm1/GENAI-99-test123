from sqlalchemy.orm import Session
from typing import List, Optional
import subprocess
import time
import socket
from ..database.models import Device
from ..utils.logger import log_db_operation, log_network_activity
from ..utils.exceptions import DeviceNotFoundException, DeviceConnectionException
from .schemas import DeviceCreate, DeviceUpdate, DevicePingResult, DevicePollResult
from ..utils.config import config
import hashlib

def get_device(db: Session, device_id: int) -> Device:
    """
    Get a device by ID
    """
    log_db_operation("SELECT", "devices", device_id)
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise DeviceNotFoundException(f"Device with ID {device_id} not found")
    return device

def get_device_by_ip(db: Session, ip_address: str) -> Device:
    """
    Get a device by IP address
    """
    log_db_operation("SELECT", "devices", f"ip:{ip_address}")
    device = db.query(Device).filter(Device.ip_address == ip_address).first()
    if not device:
        raise DeviceNotFoundException(f"Device with IP {ip_address} not found")
    return device

def get_devices(db: Session, skip: int = 0, limit: int = 100) -> List[Device]:
    """
    Get all devices with pagination
    """
    log_db_operation("SELECT", "devices", "all")
    return db.query(Device).offset(skip).limit(limit).all()

def create_device(db: Session, device: DeviceCreate) -> Device:
    """
    Create a new device
    """
    # Hash the password
    hashed_password = hashlib.sha256(device.password.encode()).hexdigest()
    
    # Create device object
    db_device = Device(
        name=device.name,
        ip_address=device.ip_address,
        device_type=device.device_type,
        username=device.username,
        hashed_password=hashed_password,
        port=device.port,
        protocol=device.protocol
    )
    
    # Add to database
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    log_db_operation("INSERT", "devices", db_device.id)
    
    return db_device

def update_device(db: Session, device_id: int, device: DeviceUpdate) -> Device:
    """
    Update a device
    """
    db_device = get_device(db, device_id)
    
    # Update fields if provided
    if device.name is not None:
        db_device.name = device.name
    if device.ip_address is not None:
        db_device.ip_address = device.ip_address
    if device.device_type is not None:
        db_device.device_type = device.device_type
    if device.username is not None:
        db_device.username = device.username
    if device.password is not None:
        # Hash the new password
        db_device.hashed_password = hashlib.sha256(device.password.encode()).hexdigest()
    if device.port is not None:
        db_device.port = device.port
    if device.protocol is not None:
        db_device.protocol = device.protocol
    
    # Commit changes
    db.commit()
    db.refresh(db_device)
    
    log_db_operation("UPDATE", "devices", device_id)
    
    return db_device

def delete_device(db: Session, device_id: int) -> bool:
    """
    Delete a device
    """
    db_device = get_device(db, device_id)
    
    # Delete from database
    db.delete(db_device)
    db.commit()
    
    log_db_operation("DELETE", "devices", device_id)
    
    return True

def ping_device(ip_address: str, timeout: int = 2) -> DevicePingResult:
    """
    Ping a device to check connectivity using ICMP.
    """
    try:
        start_time = time.time()
        # The command uses -c 1 for a single packet and -W for timeout in seconds.
        command = ['ping', '-c', '1', '-W', str(timeout), ip_address]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        response_time = (time.time() - start_time) * 1000  # in milliseconds

        if result.returncode == 0:
            log_network_activity("ping", ip_address, "success")
            return DevicePingResult(
                ip_address=ip_address,
                reachable=True,
                response_time=response_time,
                message="Device is reachable via ICMP."
            )
        else:
            log_network_activity("ping", ip_address, "failure")
            return DevicePingResult(
                ip_address=ip_address,
                reachable=False,
                response_time=None,
                message=f"Device not reachable. Reason: {result.stderr or result.stdout}"
            )
    except FileNotFoundError:
        log_network_activity("ping", ip_address, "error")
        return DevicePingResult(
            ip_address=ip_address,
            reachable=False,
            message="Ping command not found. Please ensure ICMP is supported."
        )
    except Exception as e:
        log_network_activity("ping", ip_address, "error")
        return DevicePingResult(
            ip_address=ip_address,
            reachable=False,
            message=f"An unexpected error occurred during ping: {str(e)}"
        )

def poll_device(db: Session, device_id: int) -> DevicePollResult:
    """
    Poll a device to check its status
    """
    try:
        # Get device from database
        device = get_device(db, device_id)
        
        # Ping the device
        ping_result = ping_device(device.ip_address)
        
        # Update device status
        if ping_result.reachable:
            device.status = "online"
            message = "Device is online"
        else:
            device.status = "offline"
            message = "Device is offline"
        
        device.last_polled = time.time()
        db.commit()
        
        log_network_activity("poll", device.ip_address, device.status, device_id)
        
        return DevicePollResult(
            device_id=device_id,
            status=device.status,
            message=message,
            timestamp=device.last_polled
        )
    except Exception as e:
        log_network_activity("poll", str(device_id), "error", device_id)
        return DevicePollResult(
            device_id=device_id,
            status="error",
            message=f"Polling failed: {str(e)}",
            timestamp=time.time()
        )

def ping_device_for_endpoint(db: Session, device_id: int) -> DevicePingResult:
    """
    Pings a specific device by its ID and returns the result.
    This is intended to be called from an API endpoint.
    """
    device = get_device(db, device_id)
    return ping_device(device.ip_address)

def poll_all_devices(db: Session) -> List[DevicePollResult]:
    """
    Poll all devices to check their status
    """
    devices = get_devices(db)
    results = []
    
    for device in devices:
        result = poll_device(db, device.id)
        results.append(result)
    
    return results