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