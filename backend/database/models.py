from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    devices = relationship("Device", back_populates="owner")
    chat_messages = relationship("ChatMessage", back_populates="user")

class Device(Base):
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ip_address = Column(String, index=True)
    device_type = Column(String)  # ios, iosxr, iosxe
    username = Column(String)
    hashed_password = Column(String)
    port = Column(Integer, default=22)
    protocol = Column(String, default="ssh")  # ssh, telnet
    status = Column(String, default="unknown")  # online, offline, error
    last_polled = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    owner = relationship("User", back_populates="devices")
    configurations = relationship("Configuration", back_populates="device")

class Configuration(Base):
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    content = Column(Text)
    status = Column(String, default="draft")  # draft, validated, deployed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    validated_at = Column(DateTime)
    deployed_at = Column(DateTime)
    
    # Relationships
    device = relationship("Device", back_populates="configurations")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    context = Column(Text)  # JSON string for additional context
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")

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