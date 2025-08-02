from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
import logging
import os

from backend.database.database import get_db
from backend.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    role: str = "user"

class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    is_active: bool
    created_at: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

# Auth utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not user.check_password(password):
        return None
    return user

def get_current_user(db: Session, token: str) -> Optional[User]:
    """Get current user from JWT token"""
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    try:
        # Authenticate user
        user = authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Generate JWT token
        expires_delta = timedelta(days=30 if login_data.remember else 1)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=expires_delta
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds()),
            user=user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            display_name=user_data.display_name,
            role=user_data.role
        )
        user.set_password(user_data.password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return UserResponse(**user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/verify")
async def verify_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Verify JWT token validity"""
    try:
        user = get_current_user(db, credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return {"valid": True, "user": user.to_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user information"""
    try:
        user = get_current_user(db, credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        return UserResponse(**user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.post("/logout")
async def logout():
    """Logout endpoint - client should remove token"""
    return {"message": "Logged out successfully"}

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        user = get_current_user(db, credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Verify current password
        if not user.check_password(password_data.current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.set_password(password_data.new_password)
        db.commit()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Refresh JWT token"""
    try:
        user = get_current_user(db, credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Generate new token
        expires_delta = timedelta(days=1)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=expires_delta
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(expires_delta.total_seconds())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
