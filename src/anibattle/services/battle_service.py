from collections.abc import Callable
from dataclasses import dataclass
from typing import final, override
from uuid import UUID

from numpy.random import Generator

from anibattle.db.database_entities import DbBattleMatch, DbPoolCharacter
from anibattle.models.calculations import (
    buchholz,
    sonneborn_berger,
    tiebreak,
    update_elo,
)

type MatchStep = Callable[[UUID, UUID], None]


@final
class BattleContext:
    K = 20

    def __init__(
        self,
        id: UUID,
        characters_pool: list[DbPoolCharacter],
        battles: list[DbBattleMatch],
        round_count: int,
    ):
        self.characters_pool: list[DbPoolCharacter] = characters_pool
        self.battles: list[DbBattleMatch] = battles
        self.round_count: int = round_count
        self.battle_id: UUID = id

    @property
    def total_matches(self) -> int:
        return self.round_count * (len(self.characters_pool) // 2)

    @property
    def is_finished(self) -> bool:
        return len(self.battles) >= self.total_matches

    @property
    def current_round(self) -> int:
        return len(self.battles) // (len(self.characters_pool) // 2)

    def _get_elo_step(self, elo: dict[UUID, float]) -> MatchStep:
        def step(winner_id: UUID, loser_id: UUID) -> None:
            elo[winner_id], elo[loser_id] = update_elo(
                elo[winner_id], elo[loser_id], 1.0, k_factor=self.K
            )

        return step

    def _get_played_step(self, played: dict[UUID, int]) -> MatchStep:
        def step(winner_id: UUID, loser_id: UUID) -> None:
            played[winner_id] += 1
            played[loser_id] += 1

        return step

    def _get_opponents_step(self, opponents: dict[UUID, set[UUID]]) -> MatchStep:
        def step(winner_id: UUID, loser_id: UUID) -> None:
            opponents[winner_id].add(loser_id)
            opponents[loser_id].add(winner_id)

        return step

    def _get_defeated_step(self, defeated: dict[UUID, set[UUID]]) -> MatchStep:
        def step(winner_id: UUID, loser_id: UUID) -> None:
            defeated[winner_id].add(loser_id)

        return step

    def _get_global_step(
        self,
        start_elo: dict[UUID, float],
        deltas: dict[UUID, float],
    ) -> MatchStep:
        def step(winner_id: UUID, loser_id: UUID) -> None:
            winner_elo, loser_elo = start_elo[winner_id], start_elo[loser_id]
            winner_new_elo, loser_new_elo = update_elo(
                winner_elo, loser_elo, 1.0, k_factor=self.K
            )
            deltas[winner_id] += winner_new_elo - winner_elo
            deltas[loser_id] += loser_new_elo - loser_elo

        return step

    def _build_state(self, with_global: bool) -> BattleState:
        ids = [c.id for c in self.characters_pool]
        elo = {i: 1000.0 for i in ids}
        played = {i: 0 for i in ids}
        opponents: dict[UUID, set[UUID]] = {i: set() for i in ids}
        defeated: dict[UUID, set[UUID]] = {i: set() for i in ids}

        steps = [
            self._get_elo_step(elo),
            self._get_played_step(played),
            self._get_opponents_step(opponents),
            self._get_defeated_step(defeated),
        ]

        global_delta: dict[UUID, float] | None = None
        if with_global:
            start_elo = {c.id: c.cached_elo for c in self.characters_pool}
            global_delta = {i: 0.0 for i in ids}
            steps.append(self._get_global_step(start_elo, global_delta))

        self.handle_steps(self.battles, steps)

        return BattleState(
            names={c.id: c.name for c in self.characters_pool},
            elo=elo,
            played=played,
            opponents=opponents,
            candidates=[
                c for c in self.characters_pool if played[c.id] == self.current_round
            ],
            defeated=defeated,
            global_delta=global_delta,
        )

    def calculate_state(self) -> BattleState:
        return self._build_state(with_global=False)

    def calculate_final_state(self) -> BattleState:
        if not self.is_finished:
            raise ValueError("Battle is not finished.")
        return self._build_state(with_global=True)

    @staticmethod
    def handle_steps(battles: list[DbBattleMatch], steps: list[MatchStep]) -> None:
        for battle in battles:
            for step in steps:
                step(battle.winner_id, battle.loser_id)


@dataclass
class BattleState:
    names: dict[UUID, str]
    elo: dict[UUID, float]
    played: dict[UUID, int]
    opponents: dict[UUID, set[UUID]]
    candidates: list[DbPoolCharacter]
    defeated: dict[UUID, set[UUID]]
    global_delta: dict[UUID, float] | None = None

    @override
    def __str__(self) -> str:
        candidate_ids = {c.id for c in self.candidates}
        width: int = max(4, *(len(n) for n in self.names.values()))

        lines = [f"  {'Name':<{width}}  {'Elo':>7}  {'Played':>6}  Opponents"]
        for char_id in sorted(self.names, key=lambda i: -self.elo[i]):
            mark = "*" if char_id in candidate_ids else " "
            opponents = ", ".join(
                sorted(self.names[o] for o in self.opponents[char_id])
            )
            lines.append(
                f"{mark} {self.names[char_id]:<{width}}  {self.elo[char_id]:>7.1f}  {self.played[char_id]:>6}  {opponents or '-'}"
            )
        lines.append("* - has not played in the current round yet")
        return "\n".join(lines)


def get_next_pair(
    battle_context: BattleContext, rng: Generator
) -> tuple[DbPoolCharacter, DbPoolCharacter]:

    state = battle_context.calculate_state()

    candidates, opponents, elo = state.candidates, state.opponents, state.elo

    first = max(candidates, key=lambda c: (elo[c.id], rng.random()))
    candidates.remove(first)

    pool = [c for c in candidates if c.id not in opponents[first.id]] or candidates

    second = min(
        pool,
        key=lambda c: (abs(elo[c.id] - elo[first.id]), rng.random()),
    )
    return first, second


def print_ratings(
    state: BattleState, characters: list[DbPoolCharacter], battle_id: UUID
) -> None:
    ranking = sorted(
        characters,
        key=lambda c: (
            -round(state.elo[c.id], 6),
            -round(buchholz(state.elo, state.opponents, c.id), 6),
            -round(sonneborn_berger(state.elo, state.defeated, c.id), 6),
            tiebreak(battle_id, c.id),
        ),
    )
    for place, c in enumerate(ranking, start=1):
        elo = round(state.elo[c.id], 2)
        stats = f"Elo: {elo}, Buchholz: {buchholz(state.elo, state.opponents, c.id)}, Sonneborn-Berger: {sonneborn_berger(state.elo, state.defeated, c.id)}"
        print(f"{place}. {c.name} ({stats})")
