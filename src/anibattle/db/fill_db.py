import os
from pathlib import Path

from psycopg_pool import ConnectionPool
from pydantic import TypeAdapter

from anibattle.db.database_entities import DbModel


class Seed(DbModel, frozen=True):
    anime: list[AnimeDto]


class CharacterDto(DbModel, frozen=True):
    id: str
    name: str
    image_url: str | None = None
    image_path: str | None = None


class AnimeDto(DbModel, frozen=True):
    id: str
    name: str
    image_url: str | None = None
    image_path: str | None = None
    characters: list[CharacterDto]


SEED_PATH = Path(__file__).resolve().parents[2] / "seed.json"
anime_list = TypeAdapter(list[AnimeDto]).validate_json(
    SEED_PATH.read_text(encoding="utf-8")
)

CONNECTION_URL = os.environ["CONNECTION_URL"]

with (
    ConnectionPool(CONNECTION_URL) as pool,
    pool.connection() as conn,
    conn.cursor() as cursor,
):
    cursor.executemany(
        """
        insert into public."Anime" ("Id", "Name")
        values (%s, %s)
        on conflict ("Id") do nothing
        """,
        [(anime.id, anime.name) for anime in anime_list],
    )

    cursor.executemany(
        """
        insert into public."Characters" ("Id", "Name", "AnimeId")
        values (%s, %s, %s)
        on conflict ("Id") do nothing
        """,
        [
            (character.id, character.name, anime.id)
            for anime in anime_list
            for character in anime.characters
        ],
    )
