from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DeviceSummary(BaseModel):
    """
    Schema for device summary information
    """
    total: int
    online: int
    offline: int
    error: int

class AlertSummary(BaseModel):
    """
    Schema for alert summary information
    """
    critical: int
    warning: int
    info: int

class TaskSummary(BaseModel):
    """
    Schema for task summary information
    """
    pending: int
    completed: int
    failed: int

class SystemMetrics(BaseModel):
    """
    Schema for system metrics
    """
    cpu_usage: float
    memory_usage: float
    disk_usage: float

class RecentActivity(BaseModel):
    """
    Schema for recent activity
    """
    id: int
    description: str
    timestamp: datetime
    user: str

class DashboardOverview(BaseModel):
    """
    Schema for dashboard overview
    """
    device_summary: DeviceSummary
    alert_summary: AlertSummary
    task_summary: TaskSummary
    system_metrics: SystemMetrics
    recent_activities: List[RecentActivity]

class DashboardMetrics(BaseModel):
    """
    Schema for dashboard metrics
    """
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_in: float
    network_out: float

class TimeSeriesData(BaseModel):
    """
    Schema for time series data
    """
    timestamps: List[datetime]
    values: List[float]

class ResourceUsage(BaseModel):
    """
    Schema for resource usage over time
    """
    cpu_usage: TimeSeriesData
    memory_usage: TimeSeriesData
    disk_usage: TimeSeriesData

class DashboardData(BaseModel):
    """
    Schema for complete dashboard data
    """
    overview: DashboardOverview
    resource_usage: ResourceUsage