
from anibattle.models.database_entities import Character


def update_elo(character_a: Character, character_b: Character, actual_a: float, k_factor: float = 20):
    """
    Updates the Elo ratings for both players after a match.
    
    Parameters:
    - rating_a, rating_b: Current ratings of both players.
    - actual_a: Outcome for Player A (1.0 for a win, 0.5 for a draw, 0.0 for a loss).
    - k_factor: The maximum weight adjustment per game (default 20).
    
    Returns:
    - (new_rating_a, new_rating_b)
    """

    rating_a = character_a.elo
    rating_b = character_b.elo

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