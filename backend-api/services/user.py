from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user import UserRepository
from database.models import User
from schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        return await self.user_repository.get(db, user_id)

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        return await self.user_repository.get_by_email(db, email)

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        return await self.user_repository.create_user(
            db, 
            user_data.email, 
            user_data.password  # Will be hashed in the auth service
        )

    async def update_user(self, db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        update_data = user_data.dict(exclude_unset=True)
        return await self.user_repository.update(db, user_id, update_data)

    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        return await self.user_repository.delete(db, user_id)