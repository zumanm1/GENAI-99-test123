from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.devices.service import DeviceService
from backend.operations.service import OperationService
from backend.database.models import NetworkDevice
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class DeviceCreate(BaseModel):
    name: str
    ip_address: str
    model: str
    metadata: Optional[Dict[str, Any]] = {}

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    model: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DeviceResponse(BaseModel):
    id: str
    name: str
    ip_address: str
    model: str
    status: str
    uptime: str
    uptime_seconds: int
    last_seen: Optional[str]
    has_config_backup: bool
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

@router.get("/", response_model=List[DeviceResponse])
async def get_devices(db: Session = Depends(get_db)):
    """Get all devices"""
    try:
        device_service = DeviceService(db)
        devices = device_service.get_all_devices()
        return [DeviceResponse(**device.to_dict()) for device in devices]
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=DeviceResponse)
async def create_device(
    device_data: DeviceCreate,
    user_id: str = "default_user",  # TODO: Implement proper authentication
    db: Session = Depends(get_db)
):
    """Create a new device"""
    try:
        device_service = DeviceService(db)
        device_dict = device_data.dict()
        device_dict['owner_id'] = user_id
        
        device = device_service.create_device(device_dict)
        return DeviceResponse(**device.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: Session = Depends(get_db)):
    """Get device by ID"""
    try:
        device_service = DeviceService(db)
        device = device_service.get_device_by_id(device_id)
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return DeviceResponse(**device.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """Update device"""
    try:
        device_service = DeviceService(db)
        device_dict = {k: v for k, v in device_data.dict().items() if v is not None}
        
        device = device_service.update_device(device_id, device_dict)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return DeviceResponse(**device.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{device_id}")
async def delete_device(device_id: str, db: Session = Depends(get_db)):
    """Delete device"""
    try:
        device_service = DeviceService(db)
        device_service.delete_device(device_id)
        return {"message": "Device deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/test-connectivity")
async def test_device_connectivity(device_id: str, db: Session = Depends(get_db)):
    """Test device connectivity"""
    try:
        device_service = DeviceService(db)
        result = device_service.test_connectivity(device_id, save_result=True)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error testing connectivity for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/backup-config")
async def backup_device_config(device_id: str, db: Session = Depends(get_db)):
    """Backup device configuration"""
    try:
        device_service = DeviceService(db)
        result = device_service.backup_configuration(device_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error backing up config for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}/config")
async def get_device_config(device_id: str, db: Session = Depends(get_db)):
    """Get device configuration backup"""
    try:
        device_service = DeviceService(db)
        device = device_service.get_device_by_id(device_id)
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        if not device.config_backup:
            raise HTTPException(status_code=404, detail="No configuration backup found")
        
        return {
            "device_id": device_id,
            "device_name": device.name,
            "config": device.config_backup,
            "backup_time": device.updated_at.isoformat() if device.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting config for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}/operations")
async def get_device_operations(
    device_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get operations history for a device"""
    try:
        operation_service = OperationService(db)
        operations = operation_service.get_device_operations(device_id, limit)
        
        return [
            {
                'id': op.id,
                'operation_type': op.operation_type,
                'status': op.status,
                'command': op.command,
                'result': op.result,
                'error_message': op.error_message,
                'execution_time_ms': op.execution_time_ms,
                'created_at': op.created_at.isoformat(),
                'user_id': op.user_id
            }
            for op in operations
        ]
    except Exception as e:
        logger.error(f"Error getting operations for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/overview")
async def get_device_statistics(db: Session = Depends(get_db)):
    """Get device statistics overview"""
    try:
        total_devices = db.query(NetworkDevice).count()
        online_devices = db.query(NetworkDevice).filter(NetworkDevice.status == 'online').count()
        offline_devices = db.query(NetworkDevice).filter(NetworkDevice.status == 'offline').count()
        warning_devices = db.query(NetworkDevice).filter(NetworkDevice.status == 'warning').count()
        
        # Get devices with backups
        devices_with_backup = db.query(NetworkDevice).filter(
            NetworkDevice.config_backup.isnot(None)
        ).count()
        
        return {
            'total_devices': total_devices,
            'online_devices': online_devices,
            'offline_devices': offline_devices,
            'warning_devices': warning_devices,
            'devices_with_backup': devices_with_backup,
            'online_percentage': round((online_devices / total_devices * 100) if total_devices > 0 else 0, 1),
            'backup_coverage': round((devices_with_backup / total_devices * 100) if total_devices > 0 else 0, 1)
        }
    except Exception as e:
        logger.error(f"Error getting device statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-operations/{operation}")
async def execute_bulk_operation(
    operation: str,
    device_ids: List[str],
    db: Session = Depends(get_db)
):
    """Execute bulk operations on multiple devices"""
    try:
        device_service = DeviceService(db)
        results = []
        
        for device_id in device_ids:
            try:
                if operation == "test-connectivity":
                    result = device_service.test_connectivity(device_id, save_result=True)
                elif operation == "backup-config":
                    result = device_service.backup_configuration(device_id)
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")
                
                results.append({
                    'device_id': device_id,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'device_id': device_id,
                    'success': False,
                    'error': str(e)
                })
        
        successful = sum(1 for r in results if r['success'])
        return {
            'operation': operation,
            'total_devices': len(device_ids),
            'successful': successful,
            'failed': len(device_ids) - successful,
            'results': results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing bulk operation {operation}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# All device routes are complete above
