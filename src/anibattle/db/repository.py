from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import UUID, uuid7

from psycopg import AsyncConnection
from psycopg.rows import TupleRow, class_row

from anibattle.db.entities import (
    DbBattle,
    DbBattleDetails,
    DbBattleMatch,
    DbCharacter,
    DbPoolCharacter,
    create_battle_match,
    create_dbbattle,
    create_pool_character,
)


class AsyncBattleRepository:
    def __init__(self, connection: AsyncConnection[TupleRow]):
        self.connection: AsyncConnection[TupleRow] = connection

    async def create_characters_pool(self, limit: int) -> list[DbCharacter]:
        async with self.connection.cursor(row_factory=class_row(DbCharacter)) as cur:
            _ = await cur.execute(
                """
                        select "Id", "Name", "Elo", "BattleCount", "AnimeId"
                        from public."Characters"
                        order by random()
                        limit %s
                    """,
                (limit,),
            )

            rows = await cur.fetchall()

            return rows

    async def get_battle(self, battle_id: UUID) -> DbBattle | None:
        async with self.connection.cursor(row_factory=class_row(DbBattle)) as cur:
            _ = await cur.execute(
                """
                    select "Id", "CreatedAt", "ResolvedAt", "RoundCount"
                    from public."Battles"
                    where "Id" = %s
                """,
                (battle_id,),
            )

            row = await cur.fetchone()

        return row

    async def get_characters_pool(self, battle_id: UUID) -> list[DbPoolCharacter]:
        async with self.connection.cursor(
            row_factory=class_row(DbPoolCharacter)
        ) as cur:
            _ = await cur.execute(
                """
                    select c."Id", c."Name", bp."CachedElo", c."AnimeId"
                    from public."BattlePools" bp
                    join public."Characters" c on bp."CharacterId" = c."Id"
                    where bp."BattleId" = %s
                """,
                (battle_id,),
            )

            rows = await cur.fetchall()

        return rows

    async def get_battle_matches(self, battle_id: UUID) -> list[DbBattleMatch]:
        async with self.connection.cursor(row_factory=class_row(DbBattleMatch)) as cur:
            _ = await cur.execute(
                """
                    select "Id", "BattleId", "Round", "WinnerId", "LoserId", "CreatedAt"
                    from public."BattleMatches"
                    where "BattleId" = %s
                """,
                (battle_id,),
            )

            rows = await cur.fetchall()

        return rows

    async def create_battle(self, round_count: int = 0) -> DbBattle:
        battle = create_dbbattle(round_count)

        async with self.connection.cursor(row_factory=class_row(DbBattle)) as cur:
            _ = await cur.execute(
                """
                        insert into public."Battles" ("Id", "CreatedAt", "ResolvedAt", "RoundCount")
                        values (%s, %s, %s, %s)
                        returning "Id", "CreatedAt", "ResolvedAt", "RoundCount"
                    """,
                (battle.id, battle.created_at, battle.resolved_at, battle.round_count),
            )

            row = await cur.fetchone()

        if row is None:
            raise RuntimeError("Failed to create battle.")
        return row

    async def fill_pool(self, pool: list[DbCharacter], battle_id: UUID):
        async with self.connection.cursor() as cur:
            await cur.executemany(
                """
                    insert into public."BattlePools" ("Id", "BattleId", "CharacterId", "CachedElo")
                    values (%s, %s, %s, %s)
                """,
                [
                    (uuid7(), battle_id, character.id, character.elo)
                    for character in pool
                ],
            )

    async def create_battle_with_pool(
        self, pool_size: int, round_count: int
    ) -> tuple[DbBattle, list[DbPoolCharacter]]:
        async with self.connection.transaction():
            characters_pool = await self.create_characters_pool(pool_size)

            if len(characters_pool) < 2 or len(characters_pool) % 2 != 0:
                raise ValueError(
                    "The number of characters must be even and at least 2."
                )

            battle = await self.create_battle(round_count)

            await self.fill_pool(characters_pool, battle.id)

            db_characters_pool = [
                create_pool_character(c.id, c.name, c.anime_id, c.elo)
                for c in characters_pool
            ]

        return (battle, db_characters_pool)

    async def get_battle_details(self, battle_id: UUID) -> DbBattleDetails | None:
        async with (
            self.connection.cursor(row_factory=class_row(DbBattle)) as battle_cur,
            self.connection.cursor(row_factory=class_row(DbPoolCharacter)) as pool_cur,
            self.connection.cursor(row_factory=class_row(DbBattleMatch)) as matches_cur,
            self.connection.pipeline(),
        ):
            params = (battle_id,)
            _ = await battle_cur.execute(
                """
                    select "Id", "CreatedAt", "ResolvedAt", "RoundCount"
                    from public."Battles"
                    where "Id" = %s
                """,
                params,
            )
            _ = await pool_cur.execute(
                """
                    select c."Id", c."Name", bp."CachedElo", c."AnimeId"
                    from public."BattlePools" bp
                    join public."Characters" c on bp."CharacterId" = c."Id"
                    where bp."BattleId" = %s
                """,
                params,
            )
            _ = await matches_cur.execute(
                """
                    select "Id", "BattleId", "Round", "WinnerId", "LoserId", "CreatedAt"
                    from public."BattleMatches"
                    where "BattleId" = %s
                """,
                params,
            )

            battle = await battle_cur.fetchone()

            if battle is None:
                return None

            pool = await pool_cur.fetchall()
            matches = await matches_cur.fetchall()

        return DbBattleDetails(battle, pool, matches)

    async def add_battle_match(
        self,
        battle_id: UUID,
        round_number: int,
        winner_id: UUID,
        loser_id: UUID,
    ) -> DbBattleMatch | None:
        match = create_battle_match(battle_id, round_number, winner_id, loser_id)

        async with self.connection.cursor(row_factory=class_row(DbBattleMatch)) as cur:
            _ = await cur.execute(
                """
                    insert into public."BattleMatches" ("Id", "BattleId", "Round", "WinnerId", "LoserId", "CreatedAt")
                    values (%s, %s, %s, %s, %s, %s)
                    returning "Id", "BattleId", "Round", "WinnerId", "LoserId", "CreatedAt"
                """,
                (
                    match.id,
                    match.battle_id,
                    match.round,
                    match.winner_id,
                    match.loser_id,
                    match.created_at,
                ),
            )

            row = await cur.fetchone()

        if row is None:
            return None
        return row

    async def resolve_battle(
        self, battle_id: UUID, global_delta: Mapping[UUID, float]
    ) -> bool:
        async with self.connection.transaction(), self.connection.cursor() as cur:
            _ = await cur.execute(
                """
                    update public."Battles"
                    set "ResolvedAt" = %s
                    where "Id" = %s and "ResolvedAt" is null
                """,
                (datetime.now(UTC), battle_id),
            )
            if cur.rowcount != 1:
                return False

            await cur.executemany(
                """
                    update public."Characters"
                    set "Elo" = "Elo" + %s, "BattleCount" = "BattleCount" + 1
                    where "Id" = %s
                """,
                [(delta, cid) for cid, delta in sorted(global_delta.items())],
            )
        return True
