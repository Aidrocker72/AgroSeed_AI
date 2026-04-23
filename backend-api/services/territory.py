from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.territory import TerritoryRepository
from database.models import Territory
from schemas.territory import TerritoryCreate, TerritoryUpdate


class TerritoryService:
    def __init__(self):
        self.territory_repository = TerritoryRepository()

    async def get_territory(self, db: AsyncSession, territory_id: int) -> Optional[Territory]:
        return await self.territory_repository.get(db, territory_id)

    async def get_all_territories(self, db: AsyncSession) -> List[Territory]:
        return await self.territory_repository.get_all(db)

    async def create_territory(self, db: AsyncSession, territory_data: TerritoryCreate) -> Territory:
        territory = Territory(name=territory_data.name)
        return await self.territory_repository.create(db, territory)

    async def update_territory(self, db: AsyncSession, territory_id: int, territory_data: TerritoryUpdate) -> Optional[Territory]:
        update_data = territory_data.dict(exclude_unset=True)
        return await self.territory_repository.update(db, territory_id, update_data)

    async def delete_territory(self, db: AsyncSession, territory_id: int) -> bool:
        return await self.territory_repository.delete(db, territory_id)