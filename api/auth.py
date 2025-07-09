from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.schemas import UserCreate, UserLogin, Token, User as UserSchema
from auth import (
    authenticate_user, 
    create_user, 
    create_access_token, 
    get_user_by_email, 
    get_user_by_username,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if username already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    return create_user(db=db, email=user.email, username=user.username, password=user.password)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserSchema = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.get("/verify")
async def verify_token(current_user: UserSchema = Depends(get_current_active_user)):
    """Verify if token is valid"""
    return {"valid": True, "user": current_user.email}