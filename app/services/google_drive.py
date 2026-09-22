import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.core.config import settings
from app.models.google_drive_connection import GoogleDriveConnection
from app.repositories.google_drive_repo import GoogleDriveRepository

with open(settings.GOOGLE_CLIENT_SECRETS_FILE, "r") as f:
  _raw_secrets = json.load(f)
  CLIENT_CONFIG = _raw_secrets.get("web") or _raw_secrets.get("installed")


class GoogleDriveService:

  def __init__(
      self,
      connection: GoogleDriveConnection,
      drive_repo: GoogleDriveRepository,
  ):
    self.connection = connection
    self.drive_repo = drive_repo
    self.folder_id = getattr(settings, "GOOGLE_DRIVE_FOLDER_ID", None)
    self.service = self._get_drive_service()

  def _get_drive_service(self):
    creds = Credentials(
        token=self.connection.access_token,
        refresh_token=self.connection.refresh_token,
        token_uri=CLIENT_CONFIG.get(
            "token_uri", "https://oauth2.googleapis.com/token"
        ),
        client_id=CLIENT_CONFIG["client_id"],
        client_secret=CLIENT_CONFIG["client_secret"],
        scopes=settings.GOOGLE_DRIVE_SCOPES,
    )

    if not creds.valid and creds.refresh_token:
      creds.refresh(Request())

      self.connection.access_token = creds.token
      self.connection.token_expiry = creds.expiry
      self.drive_repo.db.commit()

    return build("drive", "v3", credentials=creds, cache_discovery=False)

  def upload_file(self, file_stream, file_name: str, mime_type: str) -> dict:
    file_metadata = {
        "name": file_name,
    }
    if self.folder_id:
      file_metadata["parents"] = [self.folder_id]

    media = MediaIoBaseUpload(
        file_stream,
        mimetype=mime_type,
        resumable=True,
    )

    uploaded_file = (
        self.service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, name, webViewLink, webContentLink, size, mimeType",
        )
        .execute()
    )

    return {
        "drive_file_id": uploaded_file.get("id"),
        "drive_view_link": uploaded_file.get("webViewLink"),
    }

  def delete_file(self, drive_file_id: str) -> None:
    self.service.files().delete(fileId=drive_file_id).execute()