from fastapi import APIRouter
from .schemas import User

router = APIRouter()

@router.get("/me", response_model=User)
def read_users_me():
    """
    Get the current user's details.
    """
    # In a real implementation, this would fetch the current authenticated user.
    # For now, we'll return dummy data.
    current_user = User(
        id=1,
        username="admin",
        email="admin@example.com",
        full_name="Admin User"
    )
    return current_user
