from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    ORDINARY = "ordinary"


class UserBase(BaseModel):
    first_name: str
    last_name: str
    

class UserRegister(UserBase):
    phone_number: str
    password: str
    verification_method: str
    otp: int


class UserLogin(BaseModel):
    phone_number: str
    password: str


class UserResponse(UserBase):
    id: str
    phone_number: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Update user information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None


class UserRoleUpdate(BaseModel):
    """Change user role (admin only)"""
    role: UserRole


class UserStatusUpdate(BaseModel):
    """Activate/deactivate user (admin only)"""
    is_active: bool


class OtpRequest(BaseModel):
    phone_number: str
    otp_code: int


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)