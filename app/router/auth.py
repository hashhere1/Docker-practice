from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.users import User, Profile
from app.schema.token import Token
from app.schema.user import UserCreate, UserResponse, LoginRequest
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in : UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(or_(User.username == user_in.username , User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        ) 
    new_user = User(
        username = user_in.username,
        email = user_in.email,
        hashed_password = hash_password(user_in.password)
    )
    db.add(new_user)
    db.flush()

    new_profile = Profile(user_id = new_user.id)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_user

@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub" : str(user.id)})
    return Token(access_token=access_token, token_type="bearer")