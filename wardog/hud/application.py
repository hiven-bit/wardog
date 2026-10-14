"""HUD lifetime, tray controls and per-user settings location."""
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from wardog.hud.calibration import CalibrationWindow
from wardog.hud.config import HudCalibration, load_calibration
from wardog.hud.overlay import HudOverlay


def calibration_path() -> Path:
    return Path(QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation,
    )) / "hud.json"


class HudController:
    def __init__(self, app: QApplication, calibrate: bool = False,
                 path: Path | None = None) -> None:
        self.app = app
        self.path = path if path is not None else calibration_path()
        screen = app.primaryScreen().geometry()
        default = HudCalibration(screen.center().x(), screen.center().y())
        warning = ""
        try:
            settings = load_calibration(self.path, default)
        except (OSError, ValueError) as error:
            settings = default
            warning = f"无法读取校准，使用屏幕中心；原文件保留：{error}"
        if not any(screen.geometry().contains(settings.x, settings.y)
                   for screen in app.screens()):
            settings = HudCalibration(default.x, default.y, settings.size)
            warning = "保存的坐标不在当前屏幕内，已临时移至主屏中心。"
        self.overlay = HudOverlay(settings)
        self.overlay.show()
        self.calibration = CalibrationWindow(self.overlay, self.path)
        self.calibration.exit_requested.connect(self.shutdown)
        self.calibration.status.setText(warning)
        self.tray = QSystemTrayIcon(self.make_icon())
        self.tray.setToolTip("WarDog HUD — 右键校准或退出")
        self.menu = QMenu()
        self.menu.addAction("校准", self.show_calibration)
        self.menu.addAction("显示 / 隐藏 HUD", self.toggle_marker)
        self.menu.addSeparator()
        self.menu.addAction("退出", self.shutdown)
        self.tray.setContextMenu(self.menu)
        self.app.aboutToQuit.connect(self.close_windows)
        self.app.setQuitOnLastWindowClosed(False)
        self.has_tray = QSystemTrayIcon.isSystemTrayAvailable()
        if not self.has_tray:
            self.calibration.closed.connect(self.app.quit)
        if self.has_tray:
            self.tray.show()
        if calibrate or warning or not self.has_tray:
            self.show_calibration()

    @staticmethod
    def make_icon() -> QIcon:
        image = QPixmap(32, 32)
        image.fill(QColor("transparent"))
        painter = QPainter(image)
        painter.setPen(QPen(QColor("#00ff66"), 2))
        painter.drawEllipse(5, 5, 22, 22)
        painter.end()
        return QIcon(image)

    def show_calibration(self) -> None:
        self.calibration.sync_from_overlay()
        self.calibration.show()
        self.calibration.raise_()
        self.calibration.activateWindow()

    def toggle_marker(self) -> None:
        self.overlay.set_marker_visible(not self.overlay.isVisible())
        self.calibration.sync_from_overlay()

    def close_windows(self) -> None:
        self.tray.hide()
        self.overlay.close()
        self.calibration.close()

    def shutdown(self) -> None:
        self.close_windows()
        self.app.quit()
