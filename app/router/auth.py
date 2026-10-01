from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.auth import AuthRepository
from app.schema.token import Token
from app.schema.user import UserCreate, UserLogin, UserResponse
from app.utils.dependencies import get_auth_repo
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    auth_repo: AuthRepository = Depends(get_auth_repo),
):
    existing_user = auth_repo.get_user_by_username_or_email(user_in.username, user_in.email)
    if existing_user:
        if existing_user.username == user_in.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        if existing_user.email == user_in.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    user_data = {
        "username": user_in.username,
        "email": user_in.email,
        "hashed_password": hash_password(user_in.password),
    }
    return auth_repo.create_user(user_data)


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    auth_repo: AuthRepository = Depends(get_auth_repo),
):
    user = auth_repo.get_user_by_username(login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")