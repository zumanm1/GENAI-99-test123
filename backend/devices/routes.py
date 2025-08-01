from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.connection import get_db
from ..utils.logger import log_api_request
from ..utils.exceptions import DeviceNotFoundException, DeviceConnectionException
from .schemas import Device, DeviceCreate, DeviceUpdate, DeviceTestConnection, DevicePingResult, DevicePollResult, DevicesPollResult
from .service import get_device, get_devices, create_device, update_device, delete_device, ping_device_for_endpoint, poll_device, poll_all_devices

router = APIRouter()

@router.get("/", response_model=List[Device])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all devices
    """

    devices = get_devices(db, skip=skip, limit=limit)
    log_api_request("GET", "/devices/", status.HTTP_200_OK)
    return devices

@router.get("/{device_id}", response_model=Device)
def read_device(device_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific device by ID
    """

    try:
        device = get_device(db, device_id)
        log_api_request("GET", f"/devices/{device_id}", status.HTTP_200_OK, device_id)
        return device
    except DeviceNotFoundException as e:
        log_api_request("GET", f"/devices/{device_id}", status.HTTP_404_NOT_FOUND, device_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
def create_new_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """
    Create a new device
    """

    try:
        db_device = create_device(db, device)
        log_api_request("POST", "/devices/", status.HTTP_201_CREATED, db_device.id)
        return db_device
    except Exception as e:
        log_api_request("POST", "/devices/", status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{device_id}", response_model=Device)
def update_existing_device(device_id: int, device: DeviceUpdate, db: Session = Depends(get_db)):
    """
    Update an existing device
    """

    try:
        db_device = update_device(db, device_id, device)
        log_api_request("PUT", f"/devices/{device_id}", status.HTTP_200_OK, device_id)
        return db_device
    except DeviceNotFoundException as e:
        log_api_request("PUT", f"/devices/{device_id}", status.HTTP_404_NOT_FOUND, device_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        log_api_request("PUT", f"/devices/{device_id}", status.HTTP_400_BAD_REQUEST, device_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_device(device_id: int, db: Session = Depends(get_db)):
    """
    Delete a device
    """

    try:
        delete_device(db, device_id)
        log_api_request("DELETE", f"/devices/{device_id}", status.HTTP_204_NO_CONTENT, device_id)
        return
    except DeviceNotFoundException as e:
        log_api_request("DELETE", f"/devices/{device_id}", status.HTTP_404_NOT_FOUND, device_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{device_id}/poll", response_model=DevicePollResult)
def poll_single_device(device_id: int, db: Session = Depends(get_db)):
    """
    Poll a single device to check its status
    """

    try:
        result = poll_device(db, device_id)
        log_api_request("POST", f"/devices/{device_id}/poll", status.HTTP_200_OK, device_id)
        return result
    except DeviceNotFoundException as e:
        log_api_request("POST", f"/devices/{device_id}/poll", status.HTTP_404_NOT_FOUND, device_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/poll", response_model=DevicesPollResult)
def poll_multiple_devices(db: Session = Depends(get_db)):
    """
    Poll all devices to check their status
    """

@router.post("/{device_id}/ping", response_model=DevicePingResult)
def ping_single_device(device_id: int, db: Session = Depends(get_db)):
    """
    Ping a single device to check its reachability
    """
    try:
        result = ping_device_for_endpoint(db, device_id)
        log_api_request("POST", f"/devices/{device_id}/ping", status.HTTP_200_OK, device_id)
        return result
    except DeviceNotFoundException as e:
        log_api_request("POST", f"/devices/{device_id}/ping", status.HTTP_404_NOT_FOUND, device_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        results = poll_all_devices(db)
        successful_polls = sum(1 for result in results if result.status == "online")
        failed_polls = len(results) - successful_polls
        
        response = DevicesPollResult(
            total_devices=len(results),
            successful_polls=successful_polls,
            failed_polls=failed_polls,
            results=results
        )
        
        log_api_request("POST", "/devices/poll", status.HTTP_200_OK)
        return response
    except Exception as e:
        log_api_request("POST", "/devices/poll", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/ping", response_model=DevicePingResult)
def ping_single_device(ping_request: DeviceTestConnection):
    """
    Ping a device to check basic connectivity
    """

    try:
        result = ping_device(ping_request.ip_address)
        log_api_request("POST", "/devices/ping", status.HTTP_200_OK)
        return result
    except Exception as e:
        log_api_request("POST", "/devices/ping", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{device_id}/test-connection", response_model=DevicePingResult)
def test_device_connection(device_id: int, db: Session = Depends(get_db)):
    """
    Test connection to a specific device
    """

    try:
        device = get_device(db, device_id)
        result = ping_device(device.ip_address)
        log_api_request("POST", f"/devices/{device_id}/test-connection", status.HTTP_200_OK, device_id)
        return result
    except DeviceNotFoundException as e:
        log_api_request("POST", f"/devices/{device_id}/test-connection", status.HTTP_404_NOT_FOUND, device_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        log_api_request("POST", f"/devices/{device_id}/test-connection", status.HTTP_500_INTERNAL_SERVER_ERROR, device_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))