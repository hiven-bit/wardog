"""Validated calibration data and atomic, per-user JSON persistence."""
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import tempfile


@dataclass(frozen=True, slots=True)
class HudCalibration:
    # Global desktop logical pixels, not physical screenshot pixels.
    x: int = 960
    y: int = 540
    size: int = 40  # Outer diameter in logical pixels.

    def __post_init__(self) -> None:
        if any(type(value) is not int for value in (self.x, self.y, self.size)):
            raise ValueError("HUD coordinates and size must be integers")
        if not (-100000 <= self.x <= 100000 and -100000 <= self.y <= 100000):
            raise ValueError("HUD coordinates out of range")
        if not 12 <= self.size <= 200:
            raise ValueError("HUD size must be between 12 and 200")


def load_calibration(path: Path, default: HudCalibration) -> HudCalibration:
    """Missing files use the default; corrupt files are reported, not replaced."""
    try:
        contents = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default
    try:
        data = json.loads(contents)
        if not isinstance(data, dict) or set(data) != {"x", "y", "size"}:
            raise ValueError("Expected x, y and size fields")
        return HudCalibration(**data)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid HUD calibration file") from error


def save_calibration(path: Path, calibration: HudCalibration) -> None:
    """Replace only after writing succeeds; no partially written settings file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(asdict(calibration), stream, indent=2)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
