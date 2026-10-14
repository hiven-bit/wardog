import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from wardog.hud.application import HudController
from wardog.hud.calibration import CalibrationWindow
from wardog.hud.config import HudCalibration, load_calibration
from wardog.hud.overlay import HudOverlay


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_overlay_transparency_input_and_focus_flags(app):
    overlay = HudOverlay(HudCalibration(120, 230, 40))
    try:
        for flag in (
            Qt.WindowType.FramelessWindowHint,
            Qt.WindowType.WindowStaysOnTopHint,
            Qt.WindowType.WindowTransparentForInput,
            Qt.WindowType.WindowDoesNotAcceptFocus,
        ):
            assert overlay.windowFlags() & flag
        assert overlay.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        assert overlay.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        assert overlay.testAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        assert overlay.focusPolicy() == Qt.FocusPolicy.NoFocus
    finally:
        overlay.close()


def test_marker_renders_green_with_transparent_background(app):
    overlay = HudOverlay(HudCalibration())
    try:
        image = QImage(overlay.size(), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        overlay.render(image)
        assert image.pixelColor(0, 0).alpha() == 0
        assert image.pixelColor(image.width() // 2, image.height() // 2).alpha() == 0
        painted = [image.pixelColor(x, y) for x in range(image.width())
                   for y in range(image.height()) if image.pixelColor(x, y).alpha()]
        assert painted
        assert all(color.green() == 255 and color.red() == 0 for color in painted)
        assert not overlay.findChildren(CalibrationWindow)
    finally:
        overlay.close()


def test_marker_moves_resizes_and_hides(app):
    overlay = HudOverlay(HudCalibration(100, 200, 40))
    try:
        overlay.set_marker_visible(True)
        assert overlay.isVisible()
        overlay.set_marker_position(-200, 300)
        assert overlay.x() + overlay.width() // 2 == -200
        assert overlay.y() + overlay.height() // 2 == 300
        overlay.set_calibration(HudCalibration(600, 700, 80))
        assert overlay.width() == 88
        assert overlay.x() + overlay.width() // 2 == 600
        overlay.set_marker_visible(False)
        assert not overlay.isVisible()
    finally:
        overlay.close()


def test_calibration_controls_preview_save_and_visibility(app, tmp_path):
    path = tmp_path / "hud.json"
    overlay = HudOverlay(HudCalibration())
    overlay.show()
    controls = CalibrationWindow(overlay, path)
    try:
        controls.x.setValue(111)
        controls.y.setValue(222)
        controls.size.setValue(50)
        assert overlay.calibration == HudCalibration(111, 222, 50)
        controls.save()
        assert load_calibration(path, HudCalibration()) == overlay.calibration
        controls.visible.setChecked(False)
        assert not overlay.isVisible()
        controls.visible.setChecked(True)
        assert overlay.isVisible()
    finally:
        controls.close()
        overlay.close()


def test_save_error_is_reported(app, tmp_path):
    path = tmp_path / "not-a-directory"
    path.write_text("occupied")
    overlay = HudOverlay(HudCalibration())
    controls = CalibrationWindow(overlay, path / "hud.json")
    try:
        controls.save()
        assert "保存失败" in controls.status.text()
        assert path.read_text() == "occupied"
    finally:
        controls.close()
        overlay.close()


def test_controller_load_toggle_calibrate_and_shutdown(app, tmp_path, monkeypatch):
    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", lambda: False)
    controller = HudController(app, path=tmp_path / "hud.json")
    try:
        assert controller.calibration.isVisible()  # Safe fallback without a tray.
        controller.calibration.x.setValue(100)
        controller.calibration.y.setValue(200)
        controller.calibration.save()
        controller.toggle_marker()
        assert not controller.overlay.isVisible()
        assert not controller.calibration.visible.isChecked()
        controller.toggle_marker()
        assert controller.overlay.isVisible()
        controller.show_calibration()
        assert controller.calibration.isVisible()
        controller.calibration.exit_requested.emit()
        assert not controller.overlay.isVisible()
        assert not controller.calibration.isVisible()
    finally:
        controller.close_windows()
    restored = HudController(app, path=tmp_path / "hud.json")
    try:
        assert restored.overlay.calibration == HudCalibration(100, 200, 40)
    finally:
        restored.close_windows()


def test_bad_saved_position_is_recovered_without_overwriting(app, tmp_path, monkeypatch):
    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", lambda: False)
    path = tmp_path / "hud.json"
    path.write_text('{"x":100000,"y":100000,"size":60}')
    controller = HudController(app, path=path)
    try:
        assert app.primaryScreen().geometry().contains(
            controller.overlay.calibration.x, controller.overlay.calibration.y,
        )
        assert controller.overlay.calibration.size == 60
        assert "主屏中心" in controller.calibration.status.text()
        assert '100000' in path.read_text()
    finally:
        controller.close_windows()


def test_hud_entry_runs_and_leaves_no_visible_windows(app, monkeypatch, tmp_path):
    from PySide6.QtCore import QTimer
    import wardog.__main__ as entry
    import wardog.hud.application as hud_app

    monkeypatch.setattr(entry, "QApplication", lambda args: app)
    monkeypatch.setattr(hud_app, "calibration_path", lambda: tmp_path / "hud.json")
    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", lambda: False)
    QTimer.singleShot(150, app.quit)
    assert entry.main(["--hud", "--calibrate"]) == 0
    assert not any(window.isVisible() for window in app.topLevelWidgets())


@pytest.mark.parametrize("scale", ["1", "1.25", "1.5", "2"])
def test_logical_position_is_stable_at_common_scale_factors(scale):
    import subprocess
    import sys

    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    environment["QT_SCALE_FACTOR"] = scale
    result = subprocess.run(
        [sys.executable, "-c", """
import os
from PySide6.QtWidgets import QApplication
from wardog.hud.config import HudCalibration
from wardog.hud.overlay import HudOverlay
app = QApplication([])
hud = HudOverlay(HudCalibration(300, 400, 40))
hud.show()
app.processEvents()
assert abs(hud.devicePixelRatioF() - float(os.environ['QT_SCALE_FACTOR'])) < .01
assert hud.width() == 48
assert hud.x() + hud.width() // 2 == 300
assert hud.y() + hud.height() // 2 == 400
hud.close()
"""], env=environment, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr


def test_tray_mode_keeps_controls_optional_and_reopens_them(app, tmp_path, monkeypatch):
    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", lambda: True)
    monkeypatch.setattr(QSystemTrayIcon, "show", lambda self: None)
    controller = HudController(app, path=tmp_path / "hud.json")
    try:
        assert controller.overlay.isVisible()
        assert not controller.calibration.isVisible()
        controller.menu.actions()[0].trigger()
        assert controller.calibration.isVisible()
        controller.calibration.close()
        assert controller.overlay.isVisible()
        controller.menu.actions()[0].trigger()
        assert controller.calibration.isVisible()
        controller.menu.actions()[1].trigger()
        assert not controller.overlay.isVisible()
        controller.menu.actions()[-1].trigger()
        assert not controller.calibration.isVisible()
        assert not controller.overlay.isVisible()
    finally:
        controller.close_windows()
