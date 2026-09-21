from typing import Any, Dict, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.users import User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username_or_email(
        self, username: str, email: str
    ) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(or_(User.username == username, User.email == email))
            .first()
        )

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user_data: Dict[str, Any]) -> User:
        new_user = User(**user_data)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user