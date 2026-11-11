import asyncio
import os

import numpy
from psycopg_pool import AsyncConnectionPool

from anibattle.db.repository import AsyncBattleRepository
from anibattle.services.battle_service import (
    BattleContext,
    get_next_pair,
    print_ratings,
)


async def main():
    CONNECTION_URL = os.environ["CONNECTION_URL"]

    async with (
        AsyncConnectionPool(CONNECTION_URL, open=False) as pool,
        pool.connection() as connection,
    ):
        repository = AsyncBattleRepository(connection)
        MATCH_COUNT = 32
        round_count = BattleContext.calculate_round_count(MATCH_COUNT)
        (battle, characters) = await repository.create_battle_with_pool(MATCH_COUNT, round_count)

        generator = numpy.random.default_rng(numpy.random.randint(0, 1000))

        for _i in range(battle.round_count * (len(characters) // 2)):
            details = await repository.get_battle_details(battle.id)

            if details is None:
                raise RuntimeError("Battle not found")

            context = BattleContext.from_details(details)

            state = context.calculate_state()

            print(state)

            (candidate1, candidate2) = get_next_pair(context, generator)

            winner = candidate1 if generator.random() < 0.5 else candidate2

            loser = candidate2 if winner == candidate1 else candidate1

            _ = await repository.add_battle_match(battle.id, context.current_round, winner.id, loser.id)

        details = await repository.get_battle_details(battle.id)

        if details is None:
            raise RuntimeError("Battle not found")

        context = BattleContext.from_details(details)

        state = context.calculate_final_state()

        print(state)

        print_ratings(state, context.characters_pool, context.battle_id)

        print("Global Elo Delta:")
        if state.global_delta is None:
            raise RuntimeError("Global delta is None")
        for character in context.characters_pool:
            delta = state.global_delta[character.id]
            print(f"{character.name}: {delta:+.2f}")

        _ = await repository.resolve_battle(battle.id, state.global_delta)


if __name__ == "__main__":
    asyncio.run(main())
