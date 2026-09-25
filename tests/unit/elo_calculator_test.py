from typing import Callable

import pytest

from anibattle.models.database_entities import create_character, Character
from anibattle.models.elo_calculator import update_elo

@pytest.fixture
def make_character() -> Callable[..., Character]:
    return create_character

@pytest.mark.parametrize("a, b, actual_a, delta", 
                        [(("Ann", 1000.0), ("Bob", 1000.0), 1.0, 10),
                         (("Ann", 1000.0), ("Bob", 1000.0), 0.5, 0),
                         (("Ann", 1000.0), ("Bob", 1000.0), 0, -10),
                         (("Ann", 4000.0), ("Bob", 400.0), 1.0, 0),
                         (("Ann", 4000.0), ("Bob", 400.0), 0.5, -10),
                         (("Ann", 4000.0), ("Bob", 400.0), 0, -20),
                        ])
def test_update_elo(make_character: Callable[..., Character], a, b, actual_a: float, delta: float):
    character_a, character_b = make_character(*a), make_character(*b)

    res_a, res_b = update_elo(character_a, character_b, actual_a)

    assert res_a - character_a.elo == pytest.approx(delta, abs=0.01)
    assert res_b - character_b.elo == pytest.approx(-delta, abs=0.01)

    