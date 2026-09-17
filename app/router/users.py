from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.schema.user import UserResponse, UserUpdate
from app.utils.dependencies import get_current_user, verify_user_ownership
from app.repositories import user as user_repo

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_repo.get_all(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_repo.get_by_id(user_id, db)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(verify_user_ownership),
    db: Session = Depends(get_db),
):
    return user_repo.update(user_update, current_user, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    current_user: User = Depends(verify_user_ownership),
    db: Session = Depends(get_db),
):
    return user_repo.delete(current_user, db)