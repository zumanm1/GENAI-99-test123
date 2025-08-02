from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from backend.database.models import SystemConfig, User
import logging

logger = logging.getLogger(__name__)

class SettingsService:
    """Service for managing system settings and configuration"""

    def __init__(self, db: Session):
        self.db = db

    def get_setting(self, key: str) -> Optional[SystemConfig]:
        """Retrieve a configuration setting by key"""
        try:
            return self.db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        except Exception as e:
            logger.error(f"Error retrieving setting {key}: {e}")
            return None

    def set_setting(self, key: str, value: Dict, description: Optional[str] = None, user_id: Optional[str] = None) -> SystemConfig:
        """Set or update a configuration setting"""
        try:
            setting = self.get_setting(key)
            if setting:
                setting.config_value = value
                setting.description = description
                setting.updated_by = user_id
                setting.updated_at = datetime.now()
            else:
                setting = SystemConfig(
                    config_key=key,
                    config_value=value,
                    description=description,
                    updated_by=user_id,
                )
                self.db.add(setting)
            self.db.commit()
            logger.info(f"Set configuration key {key}")
            return setting
        except Exception as e:
            logger.error(f"Error setting configuration {key}: {e}")
            self.db.rollback()
            raise

    def delete_setting(self, key: str) -> bool:
        """Delete a configuration setting by key"""
        try:
            setting = self.get_setting(key)
            if setting:
                self.db.delete(setting)
                self.db.commit()
                logger.info(f"Deleted configuration key {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting configuration {key}: {e}")
            self.db.rollback()
            return False

    def list_settings(self) -> Dict[str, SystemConfig]:
        """List all configuration settings"""
        try:
            settings = self.db.query(SystemConfig).all()
            return {setting.config_key: setting for setting in settings}
        except Exception as e:
            logger.error(f"Error listing configurations: {e}")
            return {}

