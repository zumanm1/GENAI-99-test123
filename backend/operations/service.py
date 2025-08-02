from backend.database.models import OperationLog, NetworkDevice, User
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OperationService:
    """Service class for operations management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_recent_operations(self, limit: int = 10, user_id: Optional[str] = None) -> List[OperationLog]:
        """Get recent operations with optional user filter"""
        try:
            query = self.db.query(OperationLog)
            
            if user_id:
                query = query.filter(OperationLog.user_id == user_id)
            
            return query.order_by(desc(OperationLog.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting recent operations: {e}")
            return []
    
    def get_device_operations(self, device_id: str, limit: int = 50) -> List[OperationLog]:
        """Get operations for a specific device"""
        try:
            return self.db.query(OperationLog).filter(
                OperationLog.device_id == device_id
            ).order_by(desc(OperationLog.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting device operations: {e}")
            return []
    
    def get_operation_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get operation statistics for the last N days"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Total operations
            total_ops = self.db.query(OperationLog).filter(
                OperationLog.created_at >= start_date
            ).count()
            
            # Success/failure counts
            success_ops = self.db.query(OperationLog).filter(
                and_(
                    OperationLog.created_at >= start_date,
                    OperationLog.status == 'success'
                )
            ).count()
            
            failed_ops = self.db.query(OperationLog).filter(
                and_(
                    OperationLog.created_at >= start_date,
                    OperationLog.status == 'failed'
                )
            ).count()
            
            # Average execution time
            avg_time = self.db.query(func.avg(OperationLog.execution_time_ms)).filter(
                and_(
                    OperationLog.created_at >= start_date,
                    OperationLog.execution_time_ms.isnot(None)
                )
            ).scalar() or 0
            
            # Operations by type
            ops_by_type = self.db.query(
                OperationLog.operation_type,
                func.count(OperationLog.id).label('count')
            ).filter(
                OperationLog.created_at >= start_date
            ).group_by(OperationLog.operation_type).all()
            
            return {
                'total_operations': total_ops,
                'successful_operations': success_ops,
                'failed_operations': failed_ops,
                'success_rate': round((success_ops / total_ops * 100) if total_ops > 0 else 0, 2),
                'average_execution_time': round(avg_time, 2),
                'operations_by_type': {op.operation_type: op.count for op in ops_by_type}
            }
        except Exception as e:
            logger.error(f"Error getting operation statistics: {e}")
            return {
                'total_operations': 0,
                'successful_operations': 0,
                'failed_operations': 0,
                'success_rate': 0,
                'average_execution_time': 0,
                'operations_by_type': {}
            }
    
    def get_operations_timeline(self, days: int = 7) -> Dict[str, Any]:
        """Get operations timeline data for charts"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Group operations by day
            operations_by_day = self.db.query(
                func.date(OperationLog.created_at).label('date'),
                func.count(OperationLog.id).label('count')
            ).filter(
                OperationLog.created_at >= start_date
            ).group_by(func.date(OperationLog.created_at)).all()
            
            # Create timeline data
            labels = []
            data = []
            
            for i in range(days):
                date = (datetime.now(timezone.utc) - timedelta(days=days-1-i)).date()
                labels.append(date.strftime('%Y-%m-%d'))
                
                # Find operations for this date
                count = 0
                for op in operations_by_day:
                    if op.date == date:
                        count = op.count
                        break
                data.append(count)
            
            return {
                'labels': labels,
                'data': data
            }
        except Exception as e:
            logger.error(f"Error getting operations timeline: {e}")
            return {'labels': [], 'data': []}
    
    def get_system_uptime(self) -> Dict[str, Any]:
        """Get system uptime information"""
        try:
            # Calculate uptime based on first operation
            first_operation = self.db.query(OperationLog).order_by(
                OperationLog.created_at
            ).first()
            
            if first_operation:
                uptime_seconds = (datetime.now(timezone.utc) - first_operation.created_at).total_seconds()
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                
                return {
                    'uptime_seconds': int(uptime_seconds),
                    'uptime_formatted': f"{days}d {hours}h {minutes}m",
                    'start_time': first_operation.created_at.isoformat()
                }
            else:
                return {
                    'uptime_seconds': 0,
                    'uptime_formatted': "0d 0h 0m",
                    'start_time': datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting system uptime: {e}")
            return {
                'uptime_seconds': 0,
                'uptime_formatted': "0d 0h 0m",
                'start_time': datetime.now(timezone.utc).isoformat()
            }
    
    def create_operation_log(self, operation_data: Dict[str, Any]) -> OperationLog:
        """Create a new operation log entry"""
        try:
            log_entry = OperationLog(
                user_id=operation_data.get('user_id'),
                device_id=operation_data.get('device_id'),
                operation_type=operation_data['operation_type'],
                status=operation_data['status'],
                command=operation_data.get('command'),
                result=operation_data.get('result'),
                error_message=operation_data.get('error_message'),
                execution_time_ms=operation_data.get('execution_time_ms')
            )
            
            self.db.add(log_entry)
            self.db.commit()
            self.db.refresh(log_entry)
            
            logger.info(f"Created operation log: {log_entry.id}")
            return log_entry
        except Exception as e:
            logger.error(f"Error creating operation log: {e}")
            self.db.rollback()
            raise
    
    def get_operation_by_id(self, operation_id: str) -> Optional[OperationLog]:
        """Get operation by ID"""
        try:
            return self.db.query(OperationLog).filter(OperationLog.id == operation_id).first()
        except Exception as e:
            logger.error(f"Error getting operation by ID: {e}")
            return None
    
    def get_operations(self, skip: int = 0, limit: int = 100, status: Optional[str] = None, operation_type: Optional[str] = None) -> List[OperationLog]:
        """Get operations with filtering and pagination"""
        try:
            query = self.db.query(OperationLog)
            
            # Apply filters
            if status:
                query = query.filter(OperationLog.status == status)
            
            if operation_type:
                query = query.filter(OperationLog.operation_type == operation_type)
            
            # Apply pagination and ordering
            return query.order_by(desc(OperationLog.created_at)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting operations: {e}")
            return []
    
    def get_operations_by_status(self, status: str, limit: int = 100) -> List[OperationLog]:
        """Get operations by status"""
        try:
            return self.db.query(OperationLog).filter(
                OperationLog.status == status
            ).order_by(desc(OperationLog.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting operations by status: {e}")
            return []
    
    def get_failed_operations(self, limit: int = 50) -> List[OperationLog]:
        """Get failed operations for troubleshooting"""
        return self.get_operations_by_status('failed', limit)
    
    def get_running_operations(self) -> List[OperationLog]:
        """Get currently running operations"""
        return self.get_operations_by_status('running', 100)
    
    def update_operation_status(self, operation_id: str, status: str, result: Optional[str] = None, error_message: Optional[str] = None) -> bool:
        """Update operation status"""
        try:
            operation = self.get_operation_by_id(operation_id)
            if operation:
                operation.status = status
                if result:
                    operation.result = result
                if error_message:
                    operation.error_message = error_message
                
                self.db.commit()
                logger.info(f"Updated operation {operation_id} status to {status}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating operation status: {e}")
            self.db.rollback()
            return False
