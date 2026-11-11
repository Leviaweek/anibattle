from datetime import datetime
from uuid import UUID

from anibattle.schemas.dtos import Dto, PoolCharacterDto


class GetBattleResponse(Dto, frozen=True):
    battle_id: UUID
    round_count: int
    resolved_at: datetime | None = None
    characters_pool: list[PoolCharacterDto]


class GetBattleNotFoundResponse(Dto, frozen=True):
    detail: str = "Battle not found"
