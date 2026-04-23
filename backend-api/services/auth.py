from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from config.settings import settings
from repositories.user import UserRepository
from database.models import User


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def hash_password(self, password: str) -> str:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_by_email(db, email)
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        return await self.user_repository.get_by_email(db, email)

    async def register_user(self, db: AsyncSession, email: str, password: str) -> User:
        hashed_password = self.hash_password(password)
        return await self.user_repository.create_user(db, email, hashed_password)