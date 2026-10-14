"""Single-marker transparent overlay. No telemetry or game integration."""
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from wardog.hud.config import HudCalibration


class HudOverlay(QWidget):
    def __init__(self, calibration: HudCalibration) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.set_calibration(calibration)

    def set_calibration(self, calibration: HudCalibration) -> None:
        self.calibration = calibration
        # Padding prevents the antialiased strokes being clipped.
        side = calibration.size + 8
        self.resize(side, side)
        self.move(calibration.x - side // 2, calibration.y - side // 2)
        self.update()

    def set_marker_position(self, x: int, y: int) -> None:
        """Future calculation modules can supply global logical coordinates."""
        self.set_calibration(HudCalibration(x, y, self.calibration.size))

    def set_marker_visible(self, visible: bool) -> None:
        self.setVisible(visible)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#00ff66"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = self.calibration.size / 2 - 1
        painter.drawEllipse(center, radius, radius)
        # Four short inward ticks, leaving the marker center unobstructed.
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            painter.drawLine(
                QPointF(center.x() + dx * radius * .45,
                        center.y() + dy * radius * .45),
                QPointF(center.x() + dx * radius * .85,
                        center.y() + dy * radius * .85),
            )
