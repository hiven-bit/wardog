"""UI-independent telemetry model. Units are explicit at the boundary."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FlightData:
    altitude_m: float
    speed_kmh: float
    pitch_deg: float
    roll_deg: float
