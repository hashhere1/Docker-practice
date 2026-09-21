from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.users import Profile


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: int) -> Optional[Profile]:
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def create_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Profile:
        new_profile = Profile(user_id=user_id, **profile_data)
        self.db.add(new_profile)
        self.db.commit()
        self.db.refresh(new_profile)
        return new_profile

    def update_profile(self, profile: Profile, update_data: Dict[str, Any]) -> Profile:
        for field, value in update_data.items():
            setattr(profile, field, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete_profile(self, profile: Profile) -> None:
        self.db.delete(profile)
        self.db.commit()