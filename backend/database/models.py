from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON, BigInteger
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, INET
from datetime import datetime, timezone
from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import ipaddress

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    avatar_url = Column(Text)
    role = Column(String(50), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    devices = relationship("NetworkDevice", back_populates="owner")
    operations = relationship("OperationLog", back_populates="user")
    conversations = relationship("AIConversation", back_populates="user")
    automation_tasks = relationship("AutomationTask", back_populates="user")
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class NetworkDevice(Base):
    __tablename__ = 'network_devices'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(39), nullable=False, index=True)  # Support IPv6
    model = Column(String(100), nullable=False)
    status = Column(String(20), default='unknown')  # online, offline, warning, unknown
    uptime_seconds = Column(BigInteger, default=0)
    last_seen = Column(DateTime)
    config_backup = Column(Text)
    device_metadata = Column(JSON)
    owner_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    owner = relationship("User", back_populates="devices")
    operations = relationship("OperationLog", back_populates="device")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate IP address on creation
        if self.ip_address:
            self.validate_ip_address()
    
    def validate_ip_address(self):
        """Validate IP address format"""
        try:
            ipaddress.ip_address(self.ip_address)
        except ValueError:
            raise ValueError(f"Invalid IP address: {self.ip_address}")
    
    @property
    def uptime_formatted(self):
        """Return formatted uptime string"""
        if not self.uptime_seconds:
            return "0d 0h"
        
        days = self.uptime_seconds // 86400
        hours = (self.uptime_seconds % 86400) // 3600
        return f"{days}d {hours}h"
    
    @property
    def is_online(self):
        """Check if device is online"""
        return self.status == 'online'
    
    def update_status(self, status, uptime_seconds=None):
        """Update device status and uptime"""
        self.status = status
        self.last_seen = datetime.now(timezone.utc)
        if uptime_seconds is not None:
            self.uptime_seconds = uptime_seconds
    
    def to_dict(self):
        """Convert device to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'model': self.model,
            'status': self.status,
            'uptime': self.uptime_formatted,
            'uptime_seconds': self.uptime_seconds,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'has_config_backup': bool(self.config_backup),
            'metadata': self.device_metadata or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<NetworkDevice {self.name} ({self.ip_address})>'

class OperationLog(Base):
    __tablename__ = 'operations_log'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    device_id = Column(String(36), ForeignKey("network_devices.id"))
    operation_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, pending, running
    command = Column(Text)
    result = Column(Text)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="operations")
    device = relationship("NetworkDevice", back_populates="operations")

class AIConversation(Base):
    __tablename__ = 'ai_conversations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    session_id = Column(String(100), nullable=False)
    message_role = Column(String(20), nullable=False)  # user, assistant, system
    message_content = Column(Text, nullable=False)
    conversation_metadata = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="conversations")

class AutomationTask(Base):
    __tablename__ = 'automation_tasks'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    task_type = Column(String(50), nullable=False)
    schedule_cron = Column(String(100))
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=False)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="automation_tasks")

class SystemConfig(Base):
    __tablename__ = 'system_configs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    updated_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

# GENAI Operations Models
class AuditResult(Base):
    __tablename__ = 'audit_results'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    audit_session_id = Column(String(36), nullable=False, index=True)
    device_id = Column(String(36), ForeignKey("network_devices.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    audit_type = Column(String(50), nullable=False)  # comprehensive, security, compliance, performance
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    finding_type = Column(String(100), nullable=False)  # security_vulnerability, config_drift, etc.
    finding_title = Column(String(200), nullable=False)
    finding_description = Column(Text, nullable=False)
    affected_config_section = Column(String(100))  # interfaces, routing, acls, etc.
    current_config = Column(Text)
    recommended_config = Column(Text)
    remediation_steps = Column(JSON)  # Array of steps
    risk_score = Column(Float, default=0.0)
    compliance_framework = Column(String(50))  # pci-dss, sox, nist, etc.
    ai_analysis = Column(JSON)  # Raw AI analysis data
    status = Column(String(20), default='open')  # open, acknowledged, resolved, false_positive
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    device = relationship("NetworkDevice", backref="audit_results")
    user = relationship("User", backref="audit_results")

class BaselineConfig(Base):
    __tablename__ = 'baseline_configs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    baseline_type = Column(String(50), nullable=False)  # golden, environment, device_specific
    environment = Column(String(50))  # dev, test, prod
    device_model = Column(String(100))  # Target device model
    device_group = Column(String(50))  # core, edge, branch, access
    config_template = Column(Text, nullable=False)  # The baseline configuration
    config_sections = Column(JSON)  # Structured config sections
    compliance_rules = Column(JSON)  # Associated compliance rules
    version = Column(String(20), default='1.0')
    is_active = Column(Boolean, default=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", backref="baseline_configs")

class ConfigurationDrift(Base):
    __tablename__ = 'configuration_drift'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    device_id = Column(String(36), ForeignKey("network_devices.id"), nullable=False)
    baseline_id = Column(String(36), ForeignKey("baseline_configs.id"), nullable=False)
    drift_type = Column(String(50), nullable=False)  # addition, deletion, modification
    config_section = Column(String(100), nullable=False)
    original_config = Column(Text)
    current_config = Column(Text)
    drift_description = Column(Text)
    impact_assessment = Column(JSON)  # AI-generated impact analysis
    risk_level = Column(String(20), default='medium')
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Relationships
    device = relationship("NetworkDevice", backref="configuration_drifts")
    baseline = relationship("BaselineConfig", backref="configuration_drifts")

class TroubleshootingSession(Base):
    __tablename__ = 'troubleshooting_sessions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    session_name = Column(String(200), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    problem_description = Column(Text, nullable=False)
    problem_domain = Column(String(50), nullable=False)  # connectivity, performance, routing, security, hardware
    affected_devices = Column(JSON)  # Array of device IDs
    symptoms = Column(JSON)  # Array of observed symptoms
    diagnostic_steps = Column(JSON)  # Array of diagnostic steps taken
    ai_analysis = Column(JSON)  # AI-generated analysis and recommendations
    resolution_steps = Column(JSON)  # Steps to resolve the issue
    status = Column(String(20), default='active')  # active, resolved, escalated, closed
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    estimated_resolution_time = Column(Integer)  # Minutes
    actual_resolution_time = Column(Integer)  # Minutes
    success_rate = Column(Float)  # Percentage of successful resolutions
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", backref="troubleshooting_sessions")

class DeviceMetrics(Base):
    __tablename__ = 'device_metrics'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    device_id = Column(String(36), ForeignKey("network_devices.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # cpu, memory, interface, temperature
    metric_name = Column(String(100), nullable=False)  # cpu_utilization, memory_used, interface_rx_bytes
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))  # percent, bytes, celsius, etc.
    threshold_warning = Column(Float)
    threshold_critical = Column(Float)
    collection_method = Column(String(50))  # snmp, ssh, api
    collection_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    device = relationship("NetworkDevice", backref="device_metrics")

class ComplianceRule(Base):
    __tablename__ = 'compliance_rules'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    rule_name = Column(String(200), nullable=False)
    framework = Column(String(50), nullable=False)  # pci-dss, sox, nist, cis
    category = Column(String(100), nullable=False)  # access_control, encryption, logging
    description = Column(Text, nullable=False)
    rule_logic = Column(JSON, nullable=False)  # Rule evaluation logic
    severity = Column(String(20), default='medium')
    remediation_guidance = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AlertConfiguration(Base):
    __tablename__ = 'alert_configurations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    device_id = Column(String(36), ForeignKey("network_devices.id"))
    alert_name = Column(String(200), nullable=False)
    metric_type = Column(String(50), nullable=False)
    condition_operator = Column(String(20), nullable=False)  # gt, lt, eq, ne
    threshold_value = Column(Float, nullable=False)
    severity = Column(String(20), default='warning')  # info, warning, critical
    notification_methods = Column(JSON)  # email, slack, webhook, etc.
    escalation_rules = Column(JSON)  # Escalation configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", backref="alert_configurations")
    device = relationship("NetworkDevice", backref="alert_configurations")

# Legacy models for backward compatibility - will be migrated
class Configuration(Base):
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(36), ForeignKey("network_devices.id"))
    content = Column(Text)
    status = Column(String, default="draft")  # draft, validated, deployed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    validated_at = Column(DateTime)
    deployed_at = Column(DateTime)

class LLMSetting(Base):
    __tablename__ = 'llm_settings'
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)  # openai, groq, openrouter
    api_key = Column(String)  # encrypted
    model = Column(String)
    temperature = Column(Float, default=0.7)  # 0.0-1.0
    max_tokens = Column(Integer, default=2000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class APIKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    key = Column(String)  # encrypted
    service = Column(String)  # openai, groq, openrouter, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
