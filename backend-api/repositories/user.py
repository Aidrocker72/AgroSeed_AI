from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from repositories.base import BaseRepository
from sqlalchemy.future import select


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user