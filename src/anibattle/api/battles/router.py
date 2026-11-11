from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from anibattle.api.battles.schemas import GetBattleNotFoundResponse, GetBattleResponse
from anibattle.api.dependencies import AsyncBattleRepositoryDep
from anibattle.db.entities import DbBattle

router = APIRouter(prefix="/api/battle")


@router.get(
    "/{battle_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetBattleResponse,
    responses={404: {"model": GetBattleNotFoundResponse}},
    summary="Get battle details",
    description="Returns the details of a specific battle, including its ID, round count, resolved status, "
    + "and the pool of characters involved in the battle.",
)
async def get_battle(battle_id: UUID, repository: AsyncBattleRepositoryDep) -> GetBattleResponse:
    battle: DbBattle | None = await repository.get_battle(battle_id)
    if battle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Battle not found")

    pool = await repository.get_characters_pool(battle_id)
    dtos_pool = [character.to_dto() for character in pool]

    return GetBattleResponse(
        battle_id=battle.id,
        round_count=battle.round_count,
        resolved_at=battle.resolved_at if battle.resolved_at else None,
        characters_pool=dtos_pool,
    )
