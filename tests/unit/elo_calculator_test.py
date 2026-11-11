import pytest

from anibattle.models.calculations import update_elo


@pytest.mark.parametrize(
    "elos, actual_a, delta",
    [
        ((1000.0, 1000.0), 1.0, 10),
        ((1000.0, 1000.0), 0.5, 0),
        ((1000.0, 1000.0), 0, -10),
        ((4000.0, 400.0), 1.0, 0),
        ((4000.0, 400.0), 0.5, -10),
        ((4000.0, 400.0), 0, -20),
    ],
)
def test_update_elo(
    elos: tuple[float, float],
    actual_a: float,
    delta: float,
):
    elo_a, elo_b = elos

    res_a, res_b = update_elo(elo_a, elo_b, actual_a)

    assert res_a - elo_a == pytest.approx(delta, abs=0.01)
    assert res_b - elo_b == pytest.approx(-delta, abs=0.01)
