"""Run Qt offscreen when no desktop display is available."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from wardog.models import FlightData
from wardog.ui.window import FlightWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_window_displays_values_and_units(app):
    window = FlightWindow()
    try:
        window.display_data(FlightData(1234.5, 456.7, -8.9, 10.2))
        assert {key: label.text() for key, label in window.values.items()} == {
            "altitude_m": "1234.5 m", "speed_kmh": "456.7 km/h",
            "pitch_deg": "-8.9 °", "roll_deg": "10.2 °",
        }
    finally:
        window.close()


def test_window_starts_updates_and_stops_on_close(app):
    window = FlightWindow()
    try:
        window.show()
        assert window.isVisible()
        before = window.values["pitch_deg"].text()
        assert window.timer.isActive()
        QTest.qWait(350)
        assert window.values["pitch_deg"].text() != before
    finally:
        window.close()
    assert not window.timer.isActive()


def test_application_entry_runs_event_loop(app, monkeypatch):
    from PySide6.QtCore import QTimer
    import wardog.__main__ as entry

    # Reuse the test application; exercise main's real Qt event loop.
    monkeypatch.setattr(entry, "QApplication", lambda args: app)
    QTimer.singleShot(150, app.quit)
    assert entry.main() == 0
    for window in app.topLevelWidgets():
        window.close()
