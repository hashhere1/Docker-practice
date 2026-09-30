from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl


class GoogleDriveConnectionCreate(BaseModel):
  user_id: int
  google_email: EmailStr
  refresh_token: str
  access_token: Optional[str] = None
  token_expiry: Optional[datetime] = None


class GoogleDriveConnectionResponse(BaseModel):
  id: int
  user_id: int
  google_email: EmailStr
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class GoogleDriveAuthUrlResponse(BaseModel):
  authorization_url: str
  