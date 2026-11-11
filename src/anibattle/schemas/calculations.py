import hashlib
from uuid import UUID


def update_elo(
    rating_a: float,
    rating_b: float,
    actual_a: float,
    k_factor: float = 20,
) -> tuple[float, float]:
    """
    Updates the Elo ratings for both players after a match.

    Parameters:
    - rating_a, rating_b: Current ratings of both players.
    - actual_a: Outcome for Player A (1.0 for a win, 0.5 for a draw, 0.0 for a loss).
    - k_factor: The maximum weight adjustment per game (default 20).

    Returns:
    - (new_rating_a, new_rating_b)
    """

    expected_a = elo(rating_a, rating_b)
    expected_b = elo(rating_b, rating_a)

    actual_b = 1.0 - actual_a

    new_rating_a = rating_a + k_factor * (actual_a - expected_a)
    new_rating_b = rating_b + k_factor * (actual_b - expected_b)

    return round(new_rating_a, 2), round(new_rating_b, 2)


def elo(rating_a: float, rating_b: float) -> float:
    """
    Calculates the expected score of Player A against Player B.
    Returns a probability between 0 and 1.
    """
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def tiebreak(battle_id: UUID, character_id: UUID) -> bytes:
    return hashlib.sha256(f"{battle_id}:{character_id}".encode()).digest()


def buchholz(elo: dict[UUID, float], opponents: dict[UUID, set[UUID]], character_id: UUID) -> float:
    return sum(elo[opponent_id] for opponent_id in opponents[character_id])


def sonneborn_berger(elo: dict[UUID, float], defeated: dict[UUID, set[UUID]], character_id: UUID) -> float:
    return sum(elo[opponent_id] for opponent_id in defeated[character_id])
