from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProfileBase(BaseModel):
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    bio : Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id : int
    user_id : int
    model_config = ConfigDict(from_attributes=True)
    

