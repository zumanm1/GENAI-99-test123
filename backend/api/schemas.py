from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """
    Base schema for user information
    """
    username: str = Field(..., example="admin")
    email: str = Field(..., example="admin@example.com")

class UserCreate(UserBase):
    """
    Schema for creating a new user
    """
    password: str = Field(..., example="password123")

class UserUpdate(BaseModel):
    """
    Schema for updating user information
    """
    username: Optional[str] = Field(None, example="newadmin")
    email: Optional[str] = Field(None, example="newadmin@example.com")
    password: Optional[str] = Field(None, example="newpassword123")

class UserInDBBase(UserBase):
    """
    Base schema for user information in database
    """
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """
    Schema for user information returned to client
    """
    pass

class UserInDB(UserInDBBase):
    """
    Schema for user information in database with hashed password
    """
    hashed_password: str

class Token(BaseModel):
    """
    Schema for JWT token
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Schema for token data
    """
    username: Optional[str] = None

class LoginRequest(BaseModel):
    """
    Schema for login request
    """
    username: str = Field(..., example="admin")
    password: str = Field(..., example="password123")

class LoginResponse(BaseModel):
    """
    Schema for login response
    """
    access_token: str
    token_type: str = "bearer"
    user: User