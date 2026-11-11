import os
from pathlib import Path

from psycopg_pool import ConnectionPool
from pydantic import TypeAdapter

from anibattle.db.entities import DbModel


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


SEED_PATH = Path(__file__).resolve().parents[3] / "seed.json"

if __name__ == "__main__":
    anime_list = TypeAdapter(list[AnimeDto]).validate_json(SEED_PATH.read_text(encoding="utf-8"))

    DATABASE = os.environ["DATABASE"]
    PASSWORD = os.environ["PASSWORD"]
    USERNAME = os.environ["USERNAME"]
    HOST = os.environ["HOST"]
    PORT = os.environ["PORT"]
    CONNECTION_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

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
            [(character.id, character.name, anime.id) for anime in anime_list for character in anime.characters],
        )
