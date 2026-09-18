from typing import Any, Dict, List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.users import User


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_conflicting_user(
    db: Session,
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
        db.query(User).filter(User.id != user_id, or_(*conditions)).first()
    )


def update(db: Session, current_user: User, update_data: Dict[str, Any]) -> User:

    for field, value in update_data.items():
        setattr(current_user, field, value)
        
    db.commit()
    db.refresh(current_user)
    return current_user


def delete(db: Session, current_user: User) -> None:
    db.delete(current_user)
    db.commit()