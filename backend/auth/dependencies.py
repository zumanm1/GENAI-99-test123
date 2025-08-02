from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import User
from backend.auth.routes import verify_token
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify and decode token
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user ID from payload
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Fetch user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure current user is an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_optional_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> User | None:
    """
    Optional authentication - returns user if token is provided and valid, None otherwise
    """
    if not credentials:
        return None
        
    try:
        token = credentials.credentials
        payload = verify_token(token)
        if not payload:
            return None
            
        user_id = payload.get("user_id")
        if not user_id:
            return None
            
        user = db.query(User).filter(User.id == user_id).first()
        return user if user and user.is_active else None
        
    except Exception as e:
        logger.warning(f"Optional authentication failed: {e}")
        return None
