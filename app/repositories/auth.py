from typing import Union
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.users import User
from app.schema.user import UserCreate, LoginRequest
from app.schema.token import Token
from app.utils.security import hash_password, verify_password, create_access_token


def register_user(request: UserCreate, db: Session):
    existing_user = (
        db.query(User)
        .filter(or_(User.username == request.username, User.email == request.email))
        .first()
    )
    if existing_user:
        if existing_user.username == request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        if existing_user.email == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(request: Union[LoginRequest, OAuth2PasswordRequestForm], db: Session):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")