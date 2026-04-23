from typing import TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase


ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        stmt = select(self._model).where(self._model.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        stmt = select(self._model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(
        self, 
        db: AsyncSession, 
        id: int, 
        obj_data: dict
    ) -> Optional[ModelType]:
        db_obj = await self.get(db, id)
        if db_obj:
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        return None

    async def delete(self, db: AsyncSession, id: int) -> bool:
        db_obj = await self.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return True
        return False