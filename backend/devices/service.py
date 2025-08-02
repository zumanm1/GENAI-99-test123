from backend.database.models import NetworkDevice, OperationLog
from backend.ai.ai_service import ai_service
from sqlalchemy.orm import Session
import paramiko
import socket
import json
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class DeviceService:
    """Service class for device operations"""
    def __init__(self, db: Session):
        self.db = db

    def get_all_devices(self):
        """Get all devices"""
        return self.db.query(NetworkDevice).order_by(NetworkDevice.name).all()

    def get_device_by_id(self, device_id: str):
        """Get device by ID"""
        return self.db.query(NetworkDevice).get(device_id)

    def create_device(self, device_data: dict):
        """Create new device"""
        try:
            device = NetworkDevice(
                name=device_data['name'],
                ip_address=device_data['ip_address'],
                model=device_data['model'],
                status='unknown',
                device_metadata=device_data.get('metadata', {})
            )
            
            self.db.add(device)
            self.db.commit()
            self.db.refresh(device)
            
            # Test initial connectivity
            self.test_connectivity(device.id, save_result=True)
            
            return device
        except Exception as e:
            logger.error(f"Error creating device: {e}")
            self.db.rollback()
            raise

    def update_device(self, device_id: str, device_data: dict):
        """Update device information"""
        try:
            device = self.get_device_by_id(device_id)
            if not device:
                raise ValueError("Device not found")
            
            device.name = device_data.get('name', device.name)
            device.ip_address = device_data.get('ip_address', device.ip_address)
            device.model = device_data.get('model', device.model)
            device.device_metadata = device_data.get('metadata', device.device_metadata)
            device.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(device)
            return device
        except Exception as e:
            logger.error(f"Error updating device: {e}")
            self.db.rollback()
            raise

    def delete_device(self, device_id: str):
        """Delete device"""
        try:
            device = self.get_device_by_id(device_id)
            if not device:
                raise ValueError("Device not found")
            
            self.db.delete(device)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting device: {e}")
            self.db.rollback()
            raise

    def test_connectivity(self, device_id: str, save_result: bool = False):
        """Test device connectivity"""
        device = self.get_device_by_id(device_id)
        if not device:
            raise ValueError("Device not found")
        
        start_time = datetime.now(timezone.utc)
        result = {
            'device_id': device_id,
            'device_name': device.name,
            'ip_address': device.ip_address,
            'status': 'unknown',
            'response_time_ms': 0,
            'error': None
        }
        
        try:
            # Test basic connectivity with ping
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            start_ping = datetime.now(timezone.utc)
            connection_result = sock.connect_ex((device.ip_address, 22))  # SSH port
            end_ping = datetime.now(timezone.utc)
            
            response_time = (end_ping - start_ping).total_seconds() * 1000
            result['response_time_ms'] = round(response_time, 2)
            
            if connection_result == 0:
                result['status'] = 'online'
                device.update_status('online')
            else:
                result['status'] = 'offline'
                device.update_status('offline')
                result['error'] = 'Connection refused'
            
            sock.close()
            
        except socket.timeout:
            result['status'] = 'offline'
            result['error'] = 'Connection timeout'
            device.update_status('offline')
            
        except Exception as e:
            result['status'] = 'offline'
            result['error'] = str(e)
            device.update_status('offline')
        
        # Save operation log if requested
        if save_result:
            try:
                operation = OperationLog(
                    device_id=device_id,
                    operation_type='connectivity_test',
                    status='success' if result['status'] == 'online' else 'failed',
                    result=json.dumps(result),
                    execution_time_ms=int(result['response_time_ms'])
                )
                self.db.add(operation)
                self.db.commit()
            except Exception as e:
                logger.error(f"Error saving operation log: {e}")
                self.db.rollback()
                raise
        
        self.db.commit()
        logger.info(f"Connectivity test result for {device_id}: {result['status']}")
        return result

    def backup_configuration(self, device_id: str):
        """Backup device configuration via SSH"""
        device = self.get_device_by_id(device_id)
        if not device:
            raise ValueError("Device not found")
        
        start_time = datetime.now(timezone.utc)
        result = {
            'device_id': device_id,
            'device_name': device.name,
            'status': 'failed',
            'config_size': 0,
            'error': None
        }
        
        try:
            # SSH connection to device
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Note: In production, use proper credential management
            ssh.connect(
                device.ip_address,
                username='admin',  # Configure properly
                password='admin',  # Use secure credential storage
                timeout=30
            )
            
            # Execute show running-config command
            stdin, stdout, stderr = ssh.exec_command('show running-config')
            config_output = stdout.read().decode('utf-8')
            error_output = stderr.read().decode('utf-8')
            
            if error_output:
                raise Exception(f"Command error: {error_output}")
            
            # Save configuration backup
            device.config_backup = config_output
            device.updated_at = datetime.now(timezone.utc)
            
            result['status'] = 'success'
            result['config_size'] = len(config_output)
            
            ssh.close()
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Backup configuration error: {e}")
        
        # Save operation log
        try:
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds() * 1000
            operation = OperationLog(
                device_id=device_id,
                operation_type='config_backup',
                status=result['status'],
                command='show running-config',
                result=json.dumps(result),
                error_message=result.get('error'),
                execution_time_ms=int(execution_time)
            )
            self.db.add(operation)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving operation log: {e}")
            self.db.rollback()
            raise
        
        self.db.commit()
        return result

# Legacy functions removed to prevent conflicts with main DeviceService class
