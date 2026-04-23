from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from schemas.territory import TerritoryResponse
from services.territory import TerritoryService
from auth.jwt import JWTAuth


router = APIRouter()
territory_service = TerritoryService()
jwt_auth = JWTAuth()


@router.get("/", response_model=list[TerritoryResponse])
async def get_territories(
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(jwt_auth.get_current_user)
):
    territories = await territory_service.get_all_territories(db)
    return territories


@router.get("/{territory_id}", response_model=TerritoryResponse)
async def get_territory(
    territory_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(jwt_auth.get_current_user)
):
    territory = await territory_service.get_territory(db, territory_id)
    if not territory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territory not found"
        )
    return territory