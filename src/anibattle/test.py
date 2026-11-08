import os

import numpy
from psycopg_pool import ConnectionPool

from anibattle.db.db_service import AsyncBattleRepository
from anibattle.services.battle_service import get_next_pair, print_ratings

if __name__ == "__main__":
    CONNECTION_URL = os.environ["CONNECTION_URL"]

    with ConnectionPool(CONNECTION_URL) as pool, pool.connection() as connection:
        repository = AsyncBattleRepository(connection)
        (battle, characters) = repository.create_battle_with_pool(32)

        generator = numpy.random.default_rng(numpy.random.randint(0, 1000))

        for i in range(battle.round_count * (len(characters) // 2)):
            context = repository.get_battle_details(battle.id)

            if context is None:
                raise RuntimeError("Battle not found")

            state = context.calculate_state()

            print(state)

            (candidate1, candidate2) = get_next_pair(context, generator)

            winner = candidate1 if generator.random() < 0.5 else candidate2

            loser = candidate2 if winner == candidate1 else candidate1

            match = repository.add_battle_match(
                battle.id, context.current_round, winner.id, loser.id
            )

        context = repository.get_battle_details(battle.id)

        if context is None:
            raise RuntimeError("Battle not found")

        state = context.calculate_final_state()

        print(state)

        print_ratings(state, context.characters_pool, context.battle_id)

        print("Global Elo Delta:")
        if state.global_delta is None:
            raise RuntimeError("Global delta is None")
        for character in context.characters_pool:
            delta = state.global_delta[character.id]
            print(f"{character.name}: {delta:+.2f}")

        result = repository.resolve_battle(battle.id, state)
