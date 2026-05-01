from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from schemas.user import UserCreate, UserResponse
from services.auth import AuthService
from auth.jwt import JWTAuth
from database.models import User


router = APIRouter()
auth_service = AuthService()
jwt_auth = JWTAuth()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db_session)):
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    user = await auth_service.register_user(db, user_data.email, user_data.password)
    return user


@router.post("/login")
async def login(credentials: UserCreate, db: AsyncSession = Depends(get_db_session)):
    user = await auth_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return jwt_auth.create_token_response(user.id)


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(jwt_auth.get_current_user)):
    return jwt_auth.create_token_response(current_user.id)