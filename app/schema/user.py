from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
from app.schema.profile import ProfileResponse
from app.utils.validators import check_password, check_username



class UserBase(BaseModel):
    username : str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username between 3-50 chars",
    )
    email : EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return check_username(v)

    
class UserCreate(UserBase):
    password : str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password shoud have min 8 characters"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return check_password(v)


class UserUpdate(BaseModel):
    username : Optional[str] = Field(None, min_length=3, max_length=50)
    email : Optional[EmailStr] = None
    password : Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return check_username(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return check_password(v)



class UserResponse(UserBase):
    id : int
    profile : Optional[ProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    username: str
    password: str