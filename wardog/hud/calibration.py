"""Independent interactive calibration window; never painted onto the HUD."""
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox, QFormLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from wardog.hud.config import HudCalibration, save_calibration
from wardog.hud.overlay import HudOverlay


class CalibrationWindow(QWidget):
    exit_requested = Signal()
    closed = Signal()

    def __init__(self, overlay: HudOverlay, path: Path) -> None:
        super().__init__()
        self.overlay = overlay
        self.path = path
        self.setWindowTitle("WarDog — HUD 校准")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("桌面全局逻辑像素；调整后立即预览，点击保存持久化。"))
        form = QFormLayout()
        self.x = QSpinBox()
        self.y = QSpinBox()
        self.size = QSpinBox()
        for widget in (self.x, self.y):
            widget.setRange(-100000, 100000)
        self.size.setRange(12, 200)
        for widget, value in zip(
            (self.x, self.y, self.size),
            (overlay.calibration.x, overlay.calibration.y, overlay.calibration.size),
        ):
            widget.setValue(value)
            widget.valueChanged.connect(self.apply_preview)
        form.addRow("水平位置 X", self.x)
        form.addRow("垂直位置 Y", self.y)
        form.addRow("标记直径", self.size)
        layout.addLayout(form)
        self.visible = QCheckBox("显示 HUD")
        self.visible.setChecked(overlay.isVisible())
        self.visible.toggled.connect(overlay.set_marker_visible)
        layout.addWidget(self.visible)
        save = QPushButton("保存校准")
        save.clicked.connect(self.save)
        layout.addWidget(save)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        exit_button = QPushButton("退出程序")
        exit_button.clicked.connect(self.exit_requested.emit)
        layout.addWidget(exit_button)

    def sync_from_overlay(self) -> None:
        for widget, value in zip(
            (self.x, self.y, self.size),
            (self.overlay.calibration.x, self.overlay.calibration.y,
             self.overlay.calibration.size),
        ):
            widget.blockSignals(True)
            widget.setValue(value)
            widget.blockSignals(False)
        self.visible.blockSignals(True)
        self.visible.setChecked(self.overlay.isVisible())
        self.visible.blockSignals(False)

    def apply_preview(self) -> None:
        self.overlay.set_calibration(HudCalibration(
            self.x.value(), self.y.value(), self.size.value(),
        ))
        self.status.setText("尚未保存")

    def save(self) -> None:
        try:
            save_calibration(self.path, self.overlay.calibration)
        except OSError as error:
            self.status.setText(f"保存失败：{error}")
        else:
            self.status.setText(f"已保存：{self.path}")

    def closeEvent(self, event) -> None:
        self.closed.emit()
        super().closeEvent(event)
