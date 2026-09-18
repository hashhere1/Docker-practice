from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.users import User
from app.schema.user import UserCreate
from app.utils.security import hash_password


def get_user_by_username_or_email(username: str, email: str, db: Session):
    return (
        db.query(User)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )


def get_user_by_username(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()


def create_user(request: UserCreate, db: Session):
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user