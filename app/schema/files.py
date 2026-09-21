from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class FileResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    drive_file_id: str
    drive_view_link: Optional[str] = None
    mime_type: str
    file_size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)