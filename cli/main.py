import asyncio
import os

from numpy import random
from psycopg_pool import AsyncConnectionPool

from anibattle.db.db_service import AsyncBattleRepository
from anibattle.services.battle_service import get_next_pair


async def main():
    DATABASE = os.environ["DATABASE"]
    PASSWORD = os.environ["PASSWORD"]
    USERNAME = os.environ["USERNAME"]
    HOST = os.environ["HOST"]
    PORT = os.environ["PORT"]
    CONNECTION_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

    async with (
        AsyncConnectionPool(CONNECTION_URL, open=False) as pool,
        pool.connection() as conn,
    ):
        repository = AsyncBattleRepository(conn)

        (battle, _) = await repository.create_battle_with_pool(32)
        SEED = 42
        rng = random.default_rng(SEED)

        for _ in range(32):
            context = await repository.get_battle_details(battle.id)

            if context is None:
                raise RuntimeError("Battle not found")

            pair = get_next_pair(context, rng)
            print(f"Next pair: {pair[0].name} vs {pair[1].name}")
            state = context.calculate_state()
            print(state)
            user_input = int(input("Enter the winner (1 or 2): "))
            choice = user_input - 1
            _ = await repository.add_battle_match(
                context.battle_id,
                context.current_round,
                pair[choice].id,
                pair[1 - choice].id,
            )

        context = await repository.get_battle_details(battle.id)

        if context is None:
            raise RuntimeError("Battle not found")

        state = context.calculate_final_state()
        print(state)


if __name__ == "__main__":
    asyncio.run(main())
