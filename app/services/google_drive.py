import io
from typing import Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.core.config import settings

SCOPES = ["https://www.googleapis.com/auth/drive"]

class GoogleDriveService:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build("drive", "v3", credentials=self.credentials)
        self.folder_id = settings.GOOGLE_DRIVE_FOLDER_ID


    def upload_file(
            self,
            file_stream: io.BytesIO,
            file_name: str,
            mime_type: str,
            ) -> Dict[str, Optional[str]]:

        file_stream.seek(0)
        
        file_metadata = {
            "name": file_name,
            "parents": [self.folder_id]
        }

        media = MediaIoBaseUpload(
            file_stream,
            mimetype=mime_type,
            resumable=True
        )

        drive_file = (
            self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink, webContentLink",
            ).execute()
        )

        return {
            "drive_file_id": drive_file.get("id"),
            "drive_view_link": drive_file.get("webViewLink"),
        }

    def delete_file(self, drive_file_id: str) -> None:
        self.service.files().delete(fileId=drive_file_id).execute()