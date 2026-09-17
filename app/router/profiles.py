from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.schema.profile import ProfileResponse, ProfileCreate, ProfileUpdate
from app.utils.dependencies import get_current_user
from app.repositories import profile as profile_repo

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return profile_repo.get_profile(current_user, db)


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    profile_in: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return profile_repo.create_profile(profile_in, current_user, db)


@router.put("", response_model=ProfileResponse)
def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return profile_repo.update_profile(profile_in, current_user, db)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return profile_repo.delete_profile(current_user, db)