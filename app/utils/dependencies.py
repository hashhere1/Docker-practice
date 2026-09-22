from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.repositories.auth import AuthRepository
from app.repositories.file import FileRepository
from app.repositories.google_drive_repo import GoogleDriveRepository
from app.repositories.profile import ProfileRepository
from app.repositories.user import UserRepository
from app.services.google_drive import GoogleDriveService
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
  return UserRepository(db)


def get_auth_repo(db: Session = Depends(get_db)) -> AuthRepository:
  return AuthRepository(db)


def get_profile_repo(db: Session = Depends(get_db)) -> ProfileRepository:
  return ProfileRepository(db)


def get_file_repo(db: Session = Depends(get_db)) -> FileRepository:
  return FileRepository(db)


def get_google_drive_repo(db: Session = Depends(get_db)) -> GoogleDriveRepository:
  return GoogleDriveRepository(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
  )

  payload = decode_access_token(token)
  if payload is None:
    raise credentials_exception

  user_id: str | None = payload.get("sub")
  if user_id is None:
    raise credentials_exception

  user = user_repo.get_by_id(user_id=int(user_id))
  if user is None:
    raise credentials_exception
  return user


def verify_user_ownership(
    user_id: int = Path(..., description="The ID of the target user"),
    current_user: User = Depends(get_current_user),
) -> User:
  if current_user.id != user_id:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access or modify this account",
    )
  return current_user


def get_drive_service(
    current_user: User = Depends(get_current_user),
    drive_repo: GoogleDriveRepository = Depends(get_google_drive_repo),
) -> GoogleDriveService:

  connection = drive_repo.get_by_user_id(user_id=current_user.id)
  if not connection or not connection.refresh_token:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "Google Drive is not connected for this account. Please visit"
            " /google-drive/connect first."
        ),
    )

  return GoogleDriveService(connection=connection, drive_repo=drive_repo)