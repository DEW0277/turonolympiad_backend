import uuid
from app.database.base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from datetime import datetime, timezone
import enum


class UserRole(str, enum.Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    ORDINARY = "ordinary"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Roles and permissions
    role = Column(Enum(UserRole), default=UserRole.ORDINARY, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)