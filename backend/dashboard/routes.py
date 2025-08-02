from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.devices.service import DeviceService
from backend.operations.service import OperationService
from backend.database.models import NetworkDevice, OperationLog
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        device_service = DeviceService(db)
        operation_service = OperationService(db)
        
        # Get device statistics
        total_devices = db.query(NetworkDevice).count()
        online_devices = db.query(NetworkDevice).filter(NetworkDevice.status == 'online').count()
        offline_devices = db.query(NetworkDevice).filter(NetworkDevice.status == 'offline').count()
        warning_devices = db.query(NetworkDevice).filter(NetworkDevice.status == 'warning').count()
        
        device_stats = {
            'total': total_devices,
            'online': online_devices,
            'offline': offline_devices,
            'warning': warning_devices,
            'online_percentage': round((online_devices / total_devices * 100) if total_devices > 0 else 0, 1)
        }
        
        # Get operation statistics
        operation_stats = operation_service.get_operation_statistics()
        
        # Get system uptime
        uptime = operation_service.get_system_uptime()
        
        return {
            'devices': device_stats,
            'operations': operation_stats,
            'uptime': uptime,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device-status-chart")
async def get_device_status_chart(db: Session = Depends(get_db)):
    """Get device status chart data"""
    try:
        online_count = db.query(NetworkDevice).filter(NetworkDevice.status == 'online').count()
        offline_count = db.query(NetworkDevice).filter(NetworkDevice.status == 'offline').count()
        warning_count = db.query(NetworkDevice).filter(NetworkDevice.status == 'warning').count()
        
        return {
            'labels': ['Online', 'Offline', 'Warning'],
            'data': [online_count, offline_count, warning_count],
            'backgroundColor': ['#22c55e', '#ef4444', '#f59e0b']
        }
    except Exception as e:
        logger.error(f"Error getting device status chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/operations-timeline")
async def get_operations_timeline(days: int = 7, db: Session = Depends(get_db)):
    """Get operations timeline data"""
    try:
        operation_service = OperationService(db)
        timeline_data = operation_service.get_operations_timeline(days)
        return timeline_data
    except Exception as e:
        logger.error(f"Error getting operations timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-operations")
async def get_recent_operations(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent operations"""
    try:
        operation_service = OperationService(db)
        operations = operation_service.get_recent_operations(limit)
        
        return [
            {
                'id': op.id,
                'operation_type': op.operation_type,
                'status': op.status,
                'device_name': op.device.name if op.device else 'System',
                'command': op.command,
                'execution_time_ms': op.execution_time_ms,
                'created_at': op.created_at.isoformat(),
                'error_message': op.error_message
            }
            for op in operations
        ]
    except Exception as e:
        logger.error(f"Error getting recent operations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-actions/{action}")
async def execute_quick_action(action: str, db: Session = Depends(get_db)):
    """Execute quick actions"""
    try:
        if action == "backup-all":
            # Trigger backup for all devices
            device_service = DeviceService(db)
            devices = device_service.get_all_devices()
            results = []
            
            for device in devices:
                try:
                    result = device_service.backup_configuration(device.id)
                    results.append({
                        'device_id': device.id,
                        'device_name': device.name,
                        'success': result['status'] == 'success'
                    })
                except Exception as e:
                    results.append({
                        'device_id': device.id,
                        'device_name': device.name,
                        'success': False,
                        'error': str(e)
                    })
            
            successful = sum(1 for r in results if r['success'])
            return {
                'message': f'Backup completed for {successful}/{len(results)} devices',
                'results': results
            }
            
        elif action == "health-check":
            # Run health check on all devices
            device_service = DeviceService(db)
            devices = device_service.get_all_devices()
            results = []
            
            for device in devices:
                try:
                    result = device_service.test_connectivity(device.id, save_result=True)
                    results.append({
                        'device_id': device.id,
                        'device_name': device.name,
                        'status': result['status'],
                        'response_time': result.get('response_time_ms')
                    })
                except Exception as e:
                    results.append({
                        'device_id': device.id,
                        'device_name': device.name,
                        'status': 'error',
                        'error': str(e)
                    })
            
            online_count = sum(1 for r in results if r['status'] == 'online')
            return {
                'message': f'Health check completed: {online_count}/{len(results)} devices online',
                'results': results
            }
            
        elif action == "connectivity-test":
            # Test connectivity for all devices
            return await execute_quick_action("health-check", db)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
            
    except Exception as e:
        logger.error(f"Error executing quick action {action}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..database.connection import get_db
from ..utils.logger import log_api_request
from ..utils.exceptions import DatabaseException
from .schemas import DashboardOverview, DashboardMetrics, ResourceUsage
from .service import get_dashboard_overview, get_dashboard_metrics, get_resource_usage_history

router = APIRouter()

@router.get("/overview", response_model=DashboardOverview)
def read_dashboard_overview(db: Session = Depends(get_db)):
    """
    Get dashboard overview data
    """

    try:
        overview = get_dashboard_overview(db)
        log_api_request("GET", "/dashboard/overview", status.HTTP_200_OK)
        return overview
    except DatabaseException as e:
        log_api_request("GET", "/dashboard/overview", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/metrics", response_model=DashboardMetrics)
def read_dashboard_metrics():
    """
    Get current dashboard metrics
    """

    try:
        metrics = get_dashboard_metrics()
        log_api_request("GET", "/dashboard/metrics", status.HTTP_200_OK)
        return metrics
    except Exception as e:
        log_api_request("GET", "/dashboard/metrics", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/resource-usage", response_model=ResourceUsage)
def read_resource_usage_history(hours: int = 24):
    """
    Get resource usage history
    """

    try:
        resource_usage = get_resource_usage_history(hours)
        log_api_request("GET", "/dashboard/resource-usage", status.HTTP_200_OK)
        return resource_usage
    except Exception as e:
        log_api_request("GET", "/dashboard/resource-usage", status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/alerts")
def read_dashboard_alerts():
    """
    Get recent alerts
    """

    # In a real implementation, this would query an alerts table
    # For now, we'll return dummy data
    alerts = [
        {
            "id": 1,
            "severity": "critical",
            "message": "Device R15 is offline",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": 2,
            "severity": "warning",
            "message": "High CPU usage on R16",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    log_api_request("GET", "/dashboard/alerts", status.HTTP_200_OK)
    return alerts

@router.get("/activities")
def read_recent_activities():
    """
    Get recent activities
    """

    # In a real implementation, this would query an activities table
    # For now, we'll return dummy data
    activities = [
        {
            "id": 1,
            "description": "Configuration deployed to R15",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": "admin"
        },
        {
            "id": 2,
            "description": "Network audit completed for R16-R20",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": "admin"
        }
    ]
    
    log_api_request("GET", "/dashboard/activities", status.HTTP_200_OK)
    return activities