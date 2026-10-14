import math
from dataclasses import FrozenInstanceError

import pytest

from wardog.models import FlightData
from wardog.simulation import simulate_flight


def test_initial_sample():
    assert simulate_flight(0) == FlightData(1500, 450, 0, 0)


def test_model_is_immutable():
    data = simulate_flight(0)
    with pytest.raises(FrozenInstanceError):
        data.altitude_m = 0


def test_simulation_is_deterministic_and_changes_with_time():
    assert simulate_flight(7) == simulate_flight(7)
    assert simulate_flight(7) != simulate_flight(0)


def test_samples_stay_in_expected_ranges():
    for time in range(1000):
        data = simulate_flight(time / 10)
        assert 1200 <= data.altitude_m <= 1800
        assert 390 <= data.speed_kmh <= 510
        assert -12 <= data.pitch_deg <= 12
        assert -30 <= data.roll_deg <= 30


@pytest.mark.parametrize("time", [-1, math.inf, -math.inf, math.nan])
def test_invalid_time_is_rejected(time):
    with pytest.raises(ValueError):
        simulate_flight(time)
