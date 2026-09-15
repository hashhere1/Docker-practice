from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schema.profile import ProfileResponse

class UserBase(BaseModel):
    username : str
    email : EmailStr

class UserCreate(UserBase):
    password : str

class UserUpdate(BaseModel):
    username : Optional[str] = None
    email : Optional[EmailStr] = None
    password : Optional[str] = None

class UserResponse(UserBase):
    id : int
    profile : Optional[ProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)