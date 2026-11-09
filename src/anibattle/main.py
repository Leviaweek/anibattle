import os
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Literal, cast
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

from anibattle.db.database_entities import DbBattle, DbPoolCharacter
from anibattle.db.db_service import AsyncBattleRepository

type ServiceStatus = Literal["ok", "error"]

CONNECTION_URL = os.environ["CONNECTION_URL"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with AsyncConnectionPool(CONNECTION_URL, open=False) as pool:
        await pool.wait()
        app.state.pool = pool
        yield


app: FastAPI = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/api")


async def get_connection(request: Request) -> AsyncIterator[AsyncConnection]:
    request_app = cast(FastAPI, request.app)

    state = cast(dict[str, AsyncConnectionPool], request_app.state.__dict__)

    pool = state["pool"]

    async with pool.connection() as connection:
        yield connection


def get_battle_repository(
    connection: Annotated[AsyncConnection, Depends(get_connection)],
) -> AsyncBattleRepository:
    return AsyncBattleRepository(connection)


AsyncBattleRepositoryDep = Annotated[
    AsyncBattleRepository, Depends(get_battle_repository)
]


class HealthCheckResponse(BaseModel):
    status: ServiceStatus


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns the health status of the application.",
)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(status="ok")


class GetBattleResponse(BaseModel):
    battle_id: UUID
    round_count: int
    resolved_at: str | None = None
    characters_pool: list[DbPoolCharacter]


class GetBattleNotFoundResponse(BaseModel):
    detail: str = "Battle not found"


# ToDo: Add Dtos for get battle and define detail of the response as constant


@router.get(
    "/battle/{battle_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetBattleResponse,
    responses={404: {"model": GetBattleNotFoundResponse}},
    summary="Get battle details",
    description="Returns the details of a specific battle, including its ID, round count, resolved status, and the pool of characters involved in the battle.",
)
async def get_battle(
    battle_id: UUID, repository: AsyncBattleRepositoryDep
) -> GetBattleResponse:
    battle: DbBattle | None = await repository.get_battle(battle_id)
    if battle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Battle not found"
        )

    pool = await repository.get_characters_pool(battle_id)

    return GetBattleResponse(
        battle_id=battle.id,
        round_count=battle.round_count,
        resolved_at=battle.resolved_at.isoformat() if battle.resolved_at else None,
        characters_pool=pool,
    )


app.include_router(router)
