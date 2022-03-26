from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

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
    user_id: int
    email: EmailStr

# out schema with vote count
class PostOut(Post):
    vote_count: int

# defining a base model schema for user creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

# defining schemas for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# schemas for validating access token input and output
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: bool