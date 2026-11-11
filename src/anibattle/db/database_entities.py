import datetime
from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal

from anibattle.models.dto import PoolCharacterDto


class DbModel(BaseModel, frozen=True):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_pascal, populate_by_name=True
    )


class DbCharacter(DbModel, frozen=True):
    id: UUID
    name: str
    elo: float
    battle_count: int
    anime_id: UUID


def create_character(
    name: str, anime_id: UUID, elo: float = 1500.0, battle_count: int = 0
) -> DbCharacter:
    id: UUID = uuid7()
    return DbCharacter(
        id=id, name=name, elo=elo, battle_count=battle_count, anime_id=anime_id
    )


class DbCard(DbModel, frozen=True):
    id: UUID
    object_key: str
    created_at: datetime.datetime


def create_card(object_key: str):
    id: UUID = uuid7()
    return DbCard(
        id=id, object_key=object_key, created_at=datetime.datetime.now(datetime.UTC)
    )


class DbCharacterCard(DbModel, frozen=True):
    id: UUID
    card_id: UUID
    character_id: UUID


def create_character_card(card_id: UUID, character_id: UUID):
    id: UUID = uuid7()
    return DbCharacterCard(id=id, card_id=card_id, character_id=character_id)


class DbBattle(DbModel, frozen=True):
    id: UUID
    round_count: int
    created_at: datetime.datetime
    resolved_at: datetime.datetime | None


def create_dbbattle(round_count: int = 0) -> DbBattle:
    id: UUID = uuid7()
    return DbBattle(
        id=id,
        round_count=round_count,
        created_at=datetime.datetime.now(datetime.UTC),
        resolved_at=None,
    )


class DbBattleMatch(DbModel, frozen=True):
    id: UUID
    battle_id: UUID
    round: int
    winner_id: UUID
    loser_id: UUID
    created_at: datetime.datetime


def create_battle_match(
    battle_id: UUID, round: int, winner_id: UUID, loser_id: UUID
) -> DbBattleMatch:
    id: UUID = uuid7()
    return DbBattleMatch(
        id=id,
        battle_id=battle_id,
        round=round,
        winner_id=winner_id,
        loser_id=loser_id,
        created_at=datetime.datetime.now(datetime.UTC),
    )


class DbAnime(DbModel, frozen=True):
    id: UUID
    name: str


def create_anime(name: str) -> DbAnime:
    id: UUID = uuid7()
    return DbAnime(id=id, name=name)


class DbPoolCharacter(DbModel, frozen=True):
    id: UUID
    name: str
    cached_elo: float
    anime_id: UUID

    def to_dto(self) -> PoolCharacterDto:
        return PoolCharacterDto(
            id=self.id,
            name=self.name,
            cached_elo=self.cached_elo,
            anime_id=self.anime_id,
        )


def create_pool_character(
    id: UUID, name: str, anime_id: UUID, cached_elo: float = 1500.0
) -> DbPoolCharacter:
    return DbPoolCharacter(id=id, name=name, cached_elo=cached_elo, anime_id=anime_id)


@dataclass(frozen=True, slots=True)
class DbBattleDetails:
    battle: DbBattle
    pool: list[DbPoolCharacter]
    matches: list[DbBattleMatch]
