from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """
    Schema for user details.
    """
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None

    class Config:
        from_attributes = True
