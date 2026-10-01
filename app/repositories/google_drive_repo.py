from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.google_drive_connection import GoogleDriveConnection
from app.schema.google_drive import GoogleDriveConnectionCreate


class GoogleDriveRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[GoogleDriveConnection]:
        return(self.db.query(GoogleDriveConnection).filter(GoogleDriveConnection.user_id == user_id).first())


    def upsert_connection(
            self,
            schema: GoogleDriveConnectionCreate,
    ) -> GoogleDriveConnection:

        connection = self.get_by_user_id(user_id=schema.user_id)
        if not connection:
            connection = GoogleDriveConnection(
                user_id = schema.user_id,
                google_email = schema.google_email,
                refresh_token = schema.refresh_token
            )
            self.db.add(connection)

        connection.google_email = schema.google_email
        connection.refresh_token = schema.refresh_token
        connection.access_token = schema.access_token
        connection.token_expiry = schema.token_expiry
        connection.permission_type = schema.permission_type

        self.db.commit()
        self.db.refresh(connection)
        return connection

    def delete_by_user_id(self, user_id: int) -> bool:
        connection = self.get_by_user_id(user_id=user_id)
        if connection:
            self.db.delete(connection)
            self.db.commit()
            return True
        return False
