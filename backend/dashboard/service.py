from sqlalchemy.orm import Session
from typing import List, Dict
import psutil
import time
from datetime import datetime, timedelta

from ..database.models import NetworkDevice, Configuration
from ..utils.logger import log_db_operation
from ..utils.exceptions import DatabaseException
from .schemas import (
    DeviceSummary, AlertSummary, TaskSummary, SystemMetrics, 
    RecentActivity, DashboardOverview, DashboardMetrics, 
    TimeSeriesData, ResourceUsage
)

def get_device_summary(db: Session) -> DeviceSummary:
    """
    Get device summary information
    """
    try:
        total_devices = db.query(NetworkDevice).count()
        online_devices = db.query(NetworkDevice).filter(NetworkDevice.status == "online").count()
        offline_devices = db.query(NetworkDevice).filter(NetworkDevice.status == "offline").count()
        error_devices = db.query(NetworkDevice).filter(NetworkDevice.status == "error").count()
        
        log_db_operation("SELECT", "devices", "summary")
        
        return DeviceSummary(
            total=total_devices,
            online=online_devices,
            offline=offline_devices,
            error=error_devices
        )
    except Exception as e:
        raise DatabaseException(f"Failed to get device summary: {str(e)}")

def get_alert_summary(db: Session) -> AlertSummary:
    """
    Get alert summary information
    """
    # In a real implementation, this would query an alerts table
    # For now, we'll return dummy data
    return AlertSummary(
        critical=2,
        warning=5,
        info=10
    )

def get_task_summary(db: Session) -> TaskSummary:
    """
    Get task summary information
    """
    try:
        total_configs = db.query(Configuration).count()
        draft_configs = db.query(Configuration).filter(Configuration.status == "draft").count()
        validated_configs = db.query(Configuration).filter(Configuration.status == "validated").count()
        deployed_configs = db.query(Configuration).filter(Configuration.status == "deployed").count()
        
        log_db_operation("SELECT", "configurations", "summary")
        
        return TaskSummary(
            pending=draft_configs + validated_configs,
            completed=deployed_configs,
            failed=0  # In a real implementation, this would track failed deployments
        )
    except Exception as e:
        raise DatabaseException(f"Failed to get task summary: {str(e)}")

def get_system_metrics() -> SystemMetrics:
    """
    Get system metrics
    """
    try:
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get disk usage
        disk = psutil.disk_usage("/")
        disk_usage = (disk.used / disk.total) * 100
        
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage
        )
    except Exception as e:
        raise DatabaseException(f"Failed to get system metrics: {str(e)}")

def get_recent_activities(db: Session, limit: int = 5) -> List[RecentActivity]:
    """
    Get recent activities
    """
    # In a real implementation, this would query an activities table
    # For now, we'll return dummy data
    return [
        RecentActivity(
            id=1,
            description="Configuration deployed to R15",
            timestamp=datetime.utcnow() - timedelta(hours=2),
            user="admin"
        ),
        RecentActivity(
            id=2,
            description="Network audit completed for R16-R20",
            timestamp=datetime.utcnow() - timedelta(hours=5),
            user="admin"
        ),
        RecentActivity(
            id=3,
            description="New device R21 added",
            timestamp=datetime.utcnow() - timedelta(hours=24),
            user="admin"
        )
    ]

def get_dashboard_overview(db: Session) -> DashboardOverview:
    """
    Get dashboard overview
    """
    device_summary = get_device_summary(db)
    alert_summary = get_alert_summary(db)
    task_summary = get_task_summary(db)
    system_metrics = get_system_metrics()
    recent_activities = get_recent_activities(db)
    
    return DashboardOverview(
        device_summary=device_summary,
        alert_summary=alert_summary,
        task_summary=task_summary,
        system_metrics=system_metrics,
        recent_activities=recent_activities
    )

def get_dashboard_metrics() -> DashboardMetrics:
    """
    Get current dashboard metrics
    """
    system_metrics = get_system_metrics()
    
    # Get network usage (dummy data for now)
    network_in = 100.0
    network_out = 150.0
    
    return DashboardMetrics(
        timestamp=datetime.utcnow(),
        cpu_usage=system_metrics.cpu_usage,
        memory_usage=system_metrics.memory_usage,
        disk_usage=system_metrics.disk_usage,
        network_in=network_in,
        network_out=network_out
    )

def get_resource_usage_history(hours: int = 24) -> ResourceUsage:
    """
    Get resource usage history
    """
    # In a real implementation, this would query a metrics table
    # For now, we'll generate dummy data
    
    # Generate timestamps for the past 'hours' hours
    now = datetime.utcnow()
    timestamps = [now - timedelta(hours=i) for i in range(hours, 0, -1)]
    
    # Generate dummy CPU usage data (random values between 20-80)
    cpu_values = [20 + (i % 60) for i in range(len(timestamps))]
    
    # Generate dummy memory usage data (random values between 30-70)
    memory_values = [30 + (i % 40) for i in range(len(timestamps))]
    
    # Generate dummy disk usage data (random values between 40-90)
    disk_values = [40 + (i % 50) for i in range(len(timestamps))]
    
    return ResourceUsage(
        cpu_usage=TimeSeriesData(timestamps=timestamps, values=cpu_values),
        memory_usage=TimeSeriesData(timestamps=timestamps, values=memory_values),
        disk_usage=TimeSeriesData(timestamps=timestamps, values=disk_values)
    )