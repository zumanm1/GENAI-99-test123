from backend.database.models import AutomationTask, NetworkDevice, OperationLog, User
from backend.ai.ai_service import ai_service
from backend.operations.service import OperationService
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import json
import logging
from crontab import CronTab
import asyncio

logger = logging.getLogger(__name__)

class AutomationService:
    """Service class for automation task management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.operation_service = OperationService(db)
    
    def create_task(self, task_data: Dict[str, Any], user_id: str) -> AutomationTask:
        """Create a new automation task"""
        try:
            task = AutomationTask(
                user_id=user_id,
                name=task_data['name'],
                description=task_data.get('description'),
                task_type=task_data['task_type'],
                schedule_cron=task_data.get('schedule_cron'),
                is_active=task_data.get('is_active', True),
                config=task_data['config']
            )
            
            # Calculate next run time if cron schedule is provided
            if task.schedule_cron:
                task.next_run = self._calculate_next_run(task.schedule_cron)
            
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Created automation task: {task.id}")
            return task
        except Exception as e:
            logger.error(f"Error creating automation task: {e}")
            self.db.rollback()
            raise
    
    def get_task_by_id(self, task_id: str) -> Optional[AutomationTask]:
        """Get automation task by ID"""
        try:
            return self.db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
        except Exception as e:
            logger.error(f"Error getting task by ID: {e}")
            return None
    
    def get_user_tasks(self, user_id: str, active_only: bool = False) -> List[AutomationTask]:
        """Get automation tasks for a user"""
        try:
            query = self.db.query(AutomationTask).filter(AutomationTask.user_id == user_id)
            
            if active_only:
                query = query.filter(AutomationTask.is_active == True)
            
            return query.order_by(AutomationTask.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting user tasks: {e}")
            return []
    
    def get_due_tasks(self) -> List[AutomationTask]:
        """Get tasks that are due to run"""
        try:
            now = datetime.now(timezone.utc)
            return self.db.query(AutomationTask).filter(
                and_(
                    AutomationTask.is_active == True,
                    AutomationTask.next_run <= now,
                    AutomationTask.schedule_cron.isnot(None)
                )
            ).all()
        except Exception as e:
            logger.error(f"Error getting due tasks: {e}")
            return []
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Optional[AutomationTask]:
        """Update automation task"""
        try:
            task = self.get_task_by_id(task_id)
            if not task:
                return None
            
            # Update fields
            task.name = task_data.get('name', task.name)
            task.description = task_data.get('description', task.description)
            task.task_type = task_data.get('task_type', task.task_type)
            task.schedule_cron = task_data.get('schedule_cron', task.schedule_cron)
            task.is_active = task_data.get('is_active', task.is_active)
            task.config = task_data.get('config', task.config)
            task.updated_at = datetime.now(timezone.utc)
            
            # Recalculate next run if schedule changed
            if 'schedule_cron' in task_data and task.schedule_cron:
                task.next_run = self._calculate_next_run(task.schedule_cron)
            
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Updated automation task: {task_id}")
            return task
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            self.db.rollback()
            raise
    
    def delete_task(self, task_id: str) -> bool:
        """Delete automation task"""
        try:
            task = self.get_task_by_id(task_id)
            if not task:
                return False
            
            self.db.delete(task)
            self.db.commit()
            
            logger.info(f"Deleted automation task: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            self.db.rollback()
            return False
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute an automation task"""
        try:
            task = self.get_task_by_id(task_id)
            if not task:
                return {'success': False, 'error': 'Task not found'}
            
            # Update last run time
            task.last_run = datetime.now(timezone.utc)
            
            # Calculate next run time if scheduled
            if task.schedule_cron:
                task.next_run = self._calculate_next_run(task.schedule_cron)
            
            # Execute based on task type
            result = self._execute_task_by_type(task)
            
            self.db.commit()
            
            # Log the execution
            self.operation_service.create_operation_log({
                'user_id': task.user_id,
                'operation_type': f'automation_{task.task_type}',
                'status': 'success' if result['success'] else 'failed',
                'result': json.dumps(result),
                'error_message': result.get('error')
            })
            
            logger.info(f"Executed automation task: {task_id}")
            return result
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def _execute_task_by_type(self, task: AutomationTask) -> Dict[str, Any]:
        """Execute task based on its type"""
        try:
            config = task.config
            
            if task.task_type == 'device_backup':
                return self._execute_device_backup(config, task.user_id)
            elif task.task_type == 'health_check':
                return self._execute_health_check(config, task.user_id)
            elif task.task_type == 'config_generation':
                return self._execute_config_generation(config, task.user_id)
            elif task.task_type == 'device_monitoring':
                return self._execute_device_monitoring(config, task.user_id)
            else:
                return {'success': False, 'error': f'Unknown task type: {task.task_type}'}
        except Exception as e:
            logger.error(f"Error executing task by type: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_device_backup(self, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute device backup automation"""
        try:
            from backend.devices.service import DeviceService
            device_service = DeviceService(self.db)
            
            device_ids = config.get('device_ids', [])
            if not device_ids:
                # Backup all user devices if none specified
                devices = self.db.query(NetworkDevice).filter(NetworkDevice.owner_id == user_id).all()
                device_ids = [device.id for device in devices]
            
            results = []
            for device_id in device_ids:
                try:
                    result = device_service.backup_configuration(device_id)
                    results.append({
                        'device_id': device_id,
                        'success': result['status'] == 'success',
                        'size': result.get('config_size', 0),
                        'error': result.get('error')
                    })
                except Exception as e:
                    results.append({
                        'device_id': device_id,
                        'success': False,
                        'error': str(e)
                    })
            
            successful = sum(1 for r in results if r['success'])
            total = len(results)
            
            return {
                'success': True,
                'message': f'Backup completed: {successful}/{total} devices successful',
                'results': results
            }
        except Exception as e:
            logger.error(f"Error in device backup automation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_health_check(self, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute health check automation"""
        try:
            from backend.devices.service import DeviceService
            device_service = DeviceService(self.db)
            
            device_ids = config.get('device_ids', [])
            if not device_ids:
                devices = self.db.query(NetworkDevice).filter(NetworkDevice.owner_id == user_id).all()
                device_ids = [device.id for device in devices]
            
            results = []
            for device_id in device_ids:
                try:
                    result = device_service.test_connectivity(device_id, save_result=True)
                    results.append({
                        'device_id': device_id,
                        'device_name': result['device_name'],
                        'status': result['status'],
                        'response_time': result['response_time_ms'],
                        'error': result.get('error')
                    })
                except Exception as e:
                    results.append({
                        'device_id': device_id,
                        'status': 'error',
                        'error': str(e)
                    })
            
            online_count = sum(1 for r in results if r['status'] == 'online')
            total_count = len(results)
            
            return {
                'success': True,
                'message': f'Health check completed: {online_count}/{total_count} devices online',
                'results': results
            }
        except Exception as e:
            logger.error(f"Error in health check automation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_config_generation(self, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute configuration generation automation"""
        try:
            config_type = config.get('config_type', 'basic')
            parameters = config.get('parameters', {})
            
            # Generate configuration using AI service
            generated_config = ai_service.generate_configuration(config_type, parameters)
            
            # Validate the generated configuration if requested
            if config.get('validate', False):
                validation_result = ai_service.validate_configuration(
                    generated_config, 
                    config.get('device_type', 'ios')
                )
                
                return {
                    'success': True,
                    'message': 'Configuration generated and validated',
                    'config': generated_config,
                    'validation': validation_result
                }
            else:
                return {
                    'success': True,
                    'message': 'Configuration generated successfully',
                    'config': generated_config
                }
        except Exception as e:
            logger.error(f"Error in config generation automation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_device_monitoring(self, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute device monitoring automation"""
        try:
            # Get devices to monitor
            device_ids = config.get('device_ids', [])
            if not device_ids:
                devices = self.db.query(NetworkDevice).filter(NetworkDevice.owner_id == user_id).all()
                device_ids = [device.id for device in devices]
            
            # Collect monitoring data
            monitoring_data = []
            for device_id in device_ids:
                device = self.db.query(NetworkDevice).filter(NetworkDevice.id == device_id).first()
                if device:
                    monitoring_data.append({
                        'device_id': device_id,
                        'device_name': device.name,
                        'status': device.status,
                        'uptime': device.uptime_formatted,
                        'last_seen': device.last_seen.isoformat() if device.last_seen else None
                    })
            
            # Check for alerts based on config thresholds
            alerts = []
            for data in monitoring_data:
                if data['status'] == 'offline':
                    alerts.append({
                        'level': 'critical',
                        'device': data['device_name'],
                        'message': 'Device is offline'
                    })
                elif data['status'] == 'warning':
                    alerts.append({
                        'level': 'warning',
                        'device': data['device_name'],
                        'message': 'Device has warnings'
                    })
            
            return {
                'success': True,
                'message': f'Monitoring completed for {len(monitoring_data)} devices',
                'monitoring_data': monitoring_data,
                'alerts': alerts
            }
        except Exception as e:
            logger.error(f"Error in device monitoring automation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_next_run(self, cron_expression: str) -> datetime:
        """Calculate next run time from cron expression"""
        try:
            # Use a simple cron parser for calculating next run
            # For now, let's implement a basic fallback
            # This would be replaced with proper cron parsing logic
            
            # Basic cron validation - split into 5 parts
            parts = cron_expression.strip().split()
            if len(parts) != 5:
                raise ValueError("Invalid cron expression format")
            
            # For now, default to 1 hour from now for any cron expression
            # In a real implementation, you'd parse the cron expression properly
            return datetime.now(timezone.utc) + timedelta(hours=1)
            
        except Exception as e:
            logger.error(f"Error calculating next run time: {e}")
            # Default to 1 hour from now if cron parsing fails
            return datetime.now(timezone.utc) + timedelta(hours=1)
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get automation task statistics"""
        try:
            total_tasks = self.db.query(AutomationTask).count()
            active_tasks = self.db.query(AutomationTask).filter(AutomationTask.is_active == True).count()
            
            # Tasks by type
            tasks_by_type = self.db.query(
                AutomationTask.task_type,
                func.count(AutomationTask.id).label('count')
            ).group_by(AutomationTask.task_type).all()
            
            # Recent executions (last 24 hours)
            recent_executions = self.db.query(AutomationTask).filter(
                AutomationTask.last_run >= datetime.now(timezone.utc) - timedelta(hours=24)
            ).count()
            
            return {
                'total_tasks': total_tasks,
                'active_tasks': active_tasks,
                'inactive_tasks': total_tasks - active_tasks,
                'tasks_by_type': {task.task_type: task.count for task in tasks_by_type},
                'recent_executions': recent_executions
            }
        except Exception as e:
            logger.error(f"Error getting task statistics: {e}")
            return {
                'total_tasks': 0,
                'active_tasks': 0,
                'inactive_tasks': 0,
                'tasks_by_type': {},
                'recent_executions': 0
            }
