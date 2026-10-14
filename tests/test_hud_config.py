import json

import pytest

from wardog.hud.config import HudCalibration, load_calibration, save_calibration


def test_missing_file_uses_default(tmp_path):
    default = HudCalibration(100, 200, 32)
    assert load_calibration(tmp_path / "hud.json", default) == default


def test_calibration_saves_and_restores_and_replaces(tmp_path):
    path = tmp_path / "settings" / "hud.json"
    default = HudCalibration()
    save_calibration(path, HudCalibration(-300, 800, 60))
    assert load_calibration(path, default) == HudCalibration(-300, 800, 60)
    save_calibration(path, HudCalibration(500, 600, 20))
    assert load_calibration(path, default) == HudCalibration(500, 600, 20)
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize("data", [
    "{broken", "[]", '{"x": 1}',
    json.dumps({"x": True, "y": 1, "size": 40}),
    json.dumps({"x": 1, "y": 2, "size": 0}),
    json.dumps({"x": 1.5, "y": 2, "size": 40}),
])
def test_corrupt_settings_are_not_silently_overwritten(tmp_path, data):
    path = tmp_path / "hud.json"
    path.write_text(data)
    with pytest.raises(ValueError):
        load_calibration(path, HudCalibration())
    assert path.read_text() == data


@pytest.mark.parametrize("values", [(0, 0, 201), (100001, 0, 40), (0, 0, 11)])
def test_calibration_limits(values):
    with pytest.raises(ValueError):
        HudCalibration(*values)
