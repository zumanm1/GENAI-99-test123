from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    ip_address = Column(String, index=True, nullable=False)
    model = Column(String, nullable=False)
    status = Column(String, default="offline")
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship to user
    owner = relationship("User", back_populates="devices")
