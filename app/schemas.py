from pydantic import BaseModel, EmailStr
from datetime import datetime

# defining a base schema for client input
class PostBase(BaseModel):
    title: str
    content: str
    # will default to True if no value is passed, optional field
    published: bool = True

# need different models for different requests
# inherits from PostBase model attributes
class PostCreate(PostBase):
    pass


# defining API response model, what we return to client
class Post(PostBase):
    id: int
    created_at: datetime

# defining a base model schema for user creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime