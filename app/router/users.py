from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.schema.user import UserResponse, UserUpdate
from app.utils.dependencies import get_current_user, verify_user_ownership
from app.utils.security import hash_password
from sqlalchemy import or_

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(verify_user_ownership),
    db: Session = Depends(get_db),
):
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
            if (
                user_update.username is not None
                and conflict.username == user_update.username
            ):
                detail = "Username already in use"
            elif (
                user_update.email is not None
                and conflict.email == user_update.email
            ):
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
        current_user.hashed_password = hash_password(
            user_update.password
        )

    db.commit()
    db.refresh(current_user)

    return current_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    current_user: User = Depends(verify_user_ownership),
    db: Session = Depends(get_db)
):
    
    db.delete(current_user)
    db.commit()
    return None