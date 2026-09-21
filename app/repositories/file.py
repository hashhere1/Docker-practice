from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.files import UserFile


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, file_id: int) -> Optional[UserFile]:
        return self.db.query(UserFile).filter(UserFile.id == file_id).first()

    def get_user_file_by_id(self, file_id: int, user_id: int) -> Optional[UserFile]:
        return(self.db.query(UserFile).filter(UserFile.id == file_id, UserFile.user_id == user_id).first())

    def get_all_by_user_id(self, user_id: int) -> List[UserFile]:
        return (self.db.query(UserFile.user_id == user_id).all())

    def create(self, user_id: int, file_data: Dict[str, Any]) -> UserFile:
        record = UserFile(user_id=user_id, **file_data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, file_record: UserFile) -> None:
        self.db.delete(file_record)
        self.db.commit()
        