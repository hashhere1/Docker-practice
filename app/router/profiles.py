from fastapi import APIRouter, Depends, HTTPException, status

from app.models.users import User
from app.repositories.profile import ProfileRepository
from app.schema.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.utils.dependencies import get_current_user, get_profile_repo

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    profile = profile_repo.get_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    existing_profile = profile_repo.get_profile(current_user.id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists for this user",
        )
    return profile_repo.create_profile(
        user_id=current_user.id,
        profile_data=profile_in.model_dump(exclude_unset=True),
    )


@router.put("", response_model=ProfileResponse)
def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    profile = profile_repo.get_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    update_data = profile_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    return profile_repo.update_profile(profile=profile, update_data=update_data)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_profile(
    current_user: User = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    profile = profile_repo.get_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    profile_repo.delete_profile(profile)
    return None