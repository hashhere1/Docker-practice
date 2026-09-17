from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.users import User
from app.schema.user import UserUpdate
from app.utils.security import hash_password


def get_all(db: Session):
    return db.query(User).all()


def get_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def update(user_update: UserUpdate, current_user: User, db: Session):
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    conditions = []
    if user_update.username is not None:
        conditions.append(User.username == user_update.username)

    if user_update.email is not None:
        conditions.append(User.email == user_update.email)

    if conditions:
        conflict = (
            db.query(User)
            .filter(
                User.id != current_user.id,
                or_(*conditions),
            )
            .first()
        )

        if conflict:
            if user_update.username is not None and conflict.username == user_update.username:
                detail = "Username already in use"
            elif user_update.email is not None and conflict.email == user_update.email:
                detail = "Email already in use"
            else:
                detail = "Username or email already in use"

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail,
            )

    if user_update.username is not None:
        current_user.username = user_update.username

    if user_update.email is not None:
        current_user.email = user_update.email

    if user_update.password is not None:
        current_user.hashed_password = hash_password(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user


def delete(current_user: User, db: Session):
    db.delete(current_user)
    db.commit()
    return None