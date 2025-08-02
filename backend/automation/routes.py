from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.automation.service import AutomationService
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response validation
class TaskCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    task_type: str
    schedule_cron: Optional[str] = None
    is_active: bool = True
    config: Dict[str, Any]

class ConfigGenerationRequest(BaseModel):
    requirements: str
    device_type: str = "cisco-ios"
    target_device: Optional[str] = None
    include_comments: bool = True
    validate_syntax: bool = False
    parameters: Optional[Dict[str, Any]] = {}

class ConfigDeploymentRequest(BaseModel):
    config: str
    device_id: str
    backup_current: bool = True
    dry_run: bool = False

class TaskResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    task_type: str
    schedule_cron: Optional[str]
    is_active: bool
    created_at: str
    last_run: Optional[str]
    next_run: Optional[str]

# Automation Task Management Endpoints
@router.post("/tasks", response_model=TaskResponse)
async def create_automation_task(
    task_data: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new automation task"""
    try:
        service = AutomationService(db)
        task = service.create_task(task_data.dict(), current_user.id)
        
        return TaskResponse(
            id=str(task.id),
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            schedule_cron=task.schedule_cron,
            is_active=task.is_active,
            created_at=task.created_at.isoformat(),
            last_run=task.last_run.isoformat() if task.last_run else None,
            next_run=task.next_run.isoformat() if task.next_run else None
        )
    except Exception as e:
        logger.error(f"Error creating automation task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks", response_model=List[TaskResponse])
async def get_user_automation_tasks(
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all automation tasks for the current user"""
    try:
        service = AutomationService(db)
        tasks = service.get_user_tasks(current_user.id, active_only)
        
        return [
            TaskResponse(
                id=str(task.id),
                name=task.name,
                description=task.description,
                task_type=task.task_type,
                schedule_cron=task.schedule_cron,
                is_active=task.is_active,
                created_at=task.created_at.isoformat(),
                last_run=task.last_run.isoformat() if task.last_run else None,
                next_run=task.next_run.isoformat() if task.next_run else None
            )
            for task in tasks
        ]
    except Exception as e:
        logger.error(f"Error getting user tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_automation_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get automation task details by ID"""
    try:
        service = AutomationService(db)
        task = service.get_task_by_id(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Ensure user can only access their own tasks
        if task.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return TaskResponse(
            id=str(task.id),
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            schedule_cron=task.schedule_cron,
            is_active=task.is_active,
            created_at=task.created_at.isoformat(),
            last_run=task.last_run.isoformat() if task.last_run else None,
            next_run=task.next_run.isoformat() if task.next_run else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task by ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/execute")
async def execute_automation_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute an automation task manually"""
    try:
        service = AutomationService(db)
        task = service.get_task_by_id(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Ensure user can only execute their own tasks
        if task.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = service.execute_task(task_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def delete_automation_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an automation task"""
    try:
        service = AutomationService(db)
        task = service.get_task_by_id(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Ensure user can only delete their own tasks
        if task.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = service.delete_task(task_id)
        if success:
            return {"message": "Task deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete task")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Configuration Generation Endpoints
@router.post("/generate")
async def generate_configuration(
    request: ConfigGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate network configuration using AI with advanced pipeline"""
    try:
        from backend.network_automation.pipeline import NetworkAutomationPipeline, ConfigValidationLevel
        
        pipeline = NetworkAutomationPipeline(db)
        
        # Determine validation level based on request
        validation_level = ConfigValidationLevel.ADVANCED
        if request.validate_syntax:
            validation_level = ConfigValidationLevel.FULL
        
        # Execute the configuration generation pipeline
        result = await pipeline.execute_config_generation_pipeline(
            requirements=request.requirements,
            device_type=request.device_type,
            user_id=current_user.id,
            validation_level=validation_level,
            additional_params={
                'target_device': request.target_device,
                'include_comments': request.include_comments,
                **request.parameters
            }
        )
        
        return {
            "success": result.success,
            "message": result.message,
            "config": result.data.get('generated_config', ''),
            "validation": result.data.get('validation', {}),
            "device_type": request.device_type,
            "requirements": request.requirements,
            "pipeline_id": result.data.get('pipeline_id'),
            "execution_time": result.execution_time,
            "warnings": result.warnings,
            "errors": result.errors
        }
    except Exception as e:
        logger.error(f"Error generating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_configuration(
    config: str,
    device_type: str = "cisco-ios",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate network configuration syntax"""
    try:
        from backend.ai.ai_service import ai_service
        
        validation_result = ai_service.validate_configuration(config, device_type)
        
        return {
            "success": True,
            "validation": validation_result,
            "device_type": device_type
        }
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy")
async def deploy_configuration(
    request: ConfigDeploymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deploy configuration to a network device using advanced pipeline"""
    try:
        from backend.network_automation.pipeline import NetworkAutomationPipeline
        
        pipeline = NetworkAutomationPipeline(db)
        
        # Execute the deployment pipeline
        result = await pipeline.execute_deployment_pipeline(
            config=request.config,
            device_id=request.device_id,
            user_id=current_user.id,
            dry_run=request.dry_run,
            backup_current=request.backup_current,
            rollback_on_failure=True
        )
        
        return {
            "success": result.success,
            "message": result.message,
            "dry_run": request.dry_run,
            "device_id": request.device_id,
            "device_name": result.data.get('device_name', ''),
            "pipeline_id": result.data.get('pipeline_id'),
            "execution_time": result.execution_time,
            "pre_checks": result.data.get('pre_checks', {}),
            "deployment": result.data.get('deployment', {}),
            "post_checks": result.data.get('post_checks', {}),
            "backup": result.data.get('backup', {}),
            "warnings": result.warnings,
            "errors": result.errors
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics and Monitoring Endpoints
@router.get("/stats")
async def get_automation_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get automation statistics for the current user"""
    try:
        service = AutomationService(db)
        stats = service.get_task_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting automation statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_configuration_templates():
    """Get available configuration templates"""
    try:
        templates = [
            {
                "id": "vlan",
                "name": "Basic VLAN Setup",
                "description": "Create VLANs with basic access and trunk ports",
                "category": "switching",
                "requirements_template": "Create a VLAN for the {department_name} department with DHCP pool {network_range}"
            },
            {
                "id": "ospf",
                "name": "OSPF Configuration",
                "description": "Configure OSPF routing protocol",
                "category": "routing",
                "requirements_template": "Configure OSPF area {area_id} on all interfaces with network {network_range}"
            },
            {
                "id": "security",
                "name": "Security Hardening",
                "description": "Apply security best practices",
                "category": "security",
                "requirements_template": "Apply security hardening including SSH configuration, ACLs, and disable unused services"
            },
            {
                "id": "qos",
                "name": "Quality of Service",
                "description": "Configure QoS policies for different traffic types",
                "category": "qos",
                "requirements_template": "Configure QoS with {priority_queues} priority queues for {traffic_types}"
            },
            {
                "id": "bgp",
                "name": "BGP Configuration",
                "description": "Configure Border Gateway Protocol",
                "category": "routing",
                "requirements_template": "Configure BGP AS {as_number} with neighbors {neighbor_list}"
            }
        ]
        
        return {
            "success": True,
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Error getting configuration templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
