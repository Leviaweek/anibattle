import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

type Noneble[T] = T | None


class Dto(BaseModel, frozen=True):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_camel, populate_by_name=True
    )


class CharacterDto(Dto, frozen=True):
    id: UUID
    name: str
    elo: float
    battle_count: int


class CardDto(Dto, frozen=True):
    id: UUID
    object_key: str


class BattleDto(Dto, frozen=True):
    id: UUID
    round_count: int
    resolved_at: Noneble[datetime.datetime]


class BattleMatchDto(Dto, frozen=True):
    id: UUID
    battle_id: UUID
    round: int
    winner_id: UUID
    loser_id: UUID
    created_at: datetime.datetime


class AnimeDto(Dto, frozen=True):
    id: UUID
    name: str


class PoolCharacterDto(Dto, frozen=True):
    id: UUID
    name: str
    cached_elo: float
    anime_id: UUID
