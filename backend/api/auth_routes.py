from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import time

from ..database.connection import get_db
from ..utils.logger import log_api_request, log_security_event
from ..utils.config import config
from ..utils.exceptions import AuthenticationException, AuthorizationException
from .auth import authenticate_user, create_access_token, create_user, get_current_user, validate_token
from .schemas import UserCreate, User, LoginRequest, LoginResponse, Token

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    """
    start_time = time.time()
    
    # Authenticate user
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        log_security_event("login_failed", f"Failed login attempt for user {login_request.username}")
        log_api_request("POST", "/auth/login", status.HTTP_401_UNAUTHORIZED)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    log_security_event("login_success", f"Successful login for user {user.username}", user.id)
    log_api_request("POST", "/auth/login", status.HTTP_200_OK, user.id)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=User.from_orm(user)
    )

@router.post("/logout")
def logout():
    """
    Logout user (invalidate token)
    """
    start_time = time.time()
    # In a real implementation, we would invalidate the token
    # For now, we'll just return a success message
    log_api_request("POST", "/auth/logout", status.HTTP_200_OK)
    return {"message": "Successfully logged out"}

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    start_time = time.time()
    try:
        db_user = create_user(db, user)
        log_api_request("POST", "/auth/register", status.HTTP_201_CREATED, db_user.id)
        return db_user
    except AuthenticationException as e:
        log_api_request("POST", "/auth/register", status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/validate")
def validate_token_endpoint(token: str, db: Session = Depends(get_db)):
    """
    Validate JWT token
    """
    start_time = time.time()
    is_valid = validate_token(db, token)
    
    status_code = status.HTTP_200_OK if is_valid else status.HTTP_401_UNAUTHORIZED
    log_api_request("GET", "/auth/validate", status_code)
    
    return {"valid": is_valid}

# Uncomment the following lines when OAuth2 is implemented
# @router.get("/me", response_model=User)
# def read_users_me(current_user: User = Depends(get_current_active_user)):
#     """
#     Get current user information
#     """
#     start_time = time.time()
#     log_api_request("GET", "/auth/me", status.HTTP_200_OK, current_user.id)
#     return current_user