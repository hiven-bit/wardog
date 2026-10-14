"""Deterministic synthetic telemetry; no game or screen integration."""
import math

from wardog.models import FlightData


def simulate_flight(elapsed_seconds: float) -> FlightData:
    """Calculate a bounded sample from nonnegative elapsed simulation time."""
    if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
        raise ValueError("elapsed_seconds must be finite and nonnegative")
    return FlightData(
        altitude_m=1500 + 300 * math.sin(elapsed_seconds / 8),
        speed_kmh=450 + 60 * math.sin(elapsed_seconds / 5),
        pitch_deg=12 * math.sin(elapsed_seconds / 3),
        roll_deg=30 * math.sin(elapsed_seconds / 4),
    )
