from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token : str
    token_type: str = "bearer"

class TokenDat(BaseModel):
    user_id : Optional[int] = None
    username : Optional[str] = None