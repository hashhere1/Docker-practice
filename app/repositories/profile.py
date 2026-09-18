from sqlalchemy.orm import Session
from app.models.users import Profile, User
from app.schema.profile import ProfileCreate, ProfileUpdate


def get_profile(current_user: User, db: Session):
    return db.query(Profile).filter(Profile.user_id == current_user.id).first()


def create_profile(profile_in: ProfileCreate, current_user: User, db: Session):
    new_profile = Profile(
        user_id=current_user.id,
        **profile_in.model_dump(exclude_unset=True),
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


def update_profile(profile_in: ProfileUpdate, profile: Profile, db: Session):
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


def delete_profile(profile: Profile, db: Session):
    db.delete(profile)
    db.commit()
    return None