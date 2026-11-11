import os
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, TypedDict, cast

from fastapi import Depends, FastAPI, Request
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from psycopg_pool import AsyncConnectionPool

from anibattle.db.repository import AsyncBattleRepository

type Pool = AsyncConnectionPool[AsyncConnection[TupleRow]]


class AppState(TypedDict):
    pool: Pool


DATABASE = os.environ["DATABASE"]
PASSWORD = os.environ["PASSWORD"]
USERNAME = os.environ["USERNAME"]
HOST = os.environ["HOST"]
PORT = os.environ["PORT"]
CONNECTION_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[AppState]:
    async with AsyncConnectionPool(
        CONNECTION_URL, connection_class=AsyncConnection, open=False
    ) as pool:
        yield {"pool": pool}


async def get_pool(request: Request) -> Pool:
    state = cast("Request[AppState]", request).state
    return state["pool"]


async def get_connection(request: Request) -> AsyncIterator[AsyncConnection]:
    pool = await get_pool(request)
    async with pool.connection() as connection:
        yield connection


def get_battle_repository(
    connection: Annotated[AsyncConnection, Depends(get_connection)],
) -> AsyncBattleRepository:
    return AsyncBattleRepository(connection)


AsyncBattleRepositoryDep = Annotated[
    AsyncBattleRepository, Depends(get_battle_repository)
]
