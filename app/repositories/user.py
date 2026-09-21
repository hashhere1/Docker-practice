from typing import Any, Dict, List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.users import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
    

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    

    def get_conflicting_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        conditions = []
        if username is not None:
            conditions.append(User.username == username)
        if email is not None:
            conditions.append(User.email == email)

        if not conditions:
            return None

        return (
            self.db.query(User)
            .filter(User.id != user_id, or_(*conditions))
            .first()
        )
    

    def update(self, current_user: User, update_data: Dict[str, Any]) -> User:
        for field, value in update_data.items():
            setattr(current_user, field, value)
        self.db.commit()
        self.db.refresh(current_user)
        return current_user
    

    def delete(self, current_user: User) -> None:
        self.db.delete(current_user)
        self.db.commit()