from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.users import User
from app.repositories.user import UserRepository
from app.schema.user import UserResponse, UserUpdate
from app.utils.dependencies import get_current_user, get_user_repo, verify_user_ownership
from app.utils.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_repo: UserRepository = Depends(get_user_repo),
    _: User = Depends(get_current_user),
):
    return user_repo.get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repo),
    _: User = Depends(get_current_user),
):
    user = user_repo.get_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(verify_user_ownership),
):
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    conflict = user_repo.get_conflicting_user(
        user_id=current_user.id,
        username=user_update.username,
        email=user_update.email,
    )
    if conflict:
        if user_update.username is not None and conflict.username == user_update.username:
            detail = "Username already in use"
        elif user_update.email is not None and conflict.email == user_update.email:
            detail = "Email already in use"
        else:
            detail = "Username or email already in use"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    return user_repo.update(current_user=current_user, update_data=update_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(verify_user_ownership),
):
    user_repo.delete(current_user=current_user)
    return None