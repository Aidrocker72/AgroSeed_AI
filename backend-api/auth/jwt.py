from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import settings
from database.connection import get_db_session
from database.models import User
from repositories.user import UserRepository


security = HTTPBearer()


class JWTAuth:
    def __init__(self):
        self.user_repository = UserRepository()

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db_session)
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                credentials.credentials, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            user_id: int = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = await self.user_repository.get(db, user_id)
        if user is None:
            raise credentials_exception
        return user

    def create_token_response(self, user_id: int):
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}