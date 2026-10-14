"""Qt window consuming the model without implementing flight calculations."""
from PySide6.QtCore import QElapsedTimer, QTimer
from PySide6.QtWidgets import (
    QFormLayout, QLabel, QMainWindow, QVBoxLayout, QWidget,
)

from wardog.models import FlightData
from wardog.simulation import simulate_flight


class FlightWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WarDog — Flight Data Demo")
        self.resize(480, 320)
        container = QWidget()
        layout = QVBoxLayout(container)
        title = QLabel("WarDog 飞行数据演示")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(QLabel("模拟数据 · 未连接游戏"))
        form = QFormLayout()
        self.values: dict[str, QLabel] = {}
        for key, caption in (
            ("altitude_m", "高度"), ("speed_kmh", "速度"),
            ("pitch_deg", "俯仰角"), ("roll_deg", "滚转角"),
        ):
            label = QLabel()
            label.setStyleSheet("font-size: 20px; font-family: monospace;")
            self.values[key] = label
            form.addRow(caption, label)
        layout.addLayout(form)
        layout.addWidget(QLabel("数据每 100 ms 更新，关闭窗口退出。"))
        self.setCentralWidget(container)
        self.clock = QElapsedTimer()
        self.clock.start()
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_telemetry)
        self.update_telemetry()
        self.timer.start()

    def display_data(self, data: FlightData) -> None:
        for key, unit in (
            ("altitude_m", "m"), ("speed_kmh", "km/h"),
            ("pitch_deg", "°"), ("roll_deg", "°"),
        ):
            self.values[key].setText(f"{getattr(data, key):.1f} {unit}")

    def update_telemetry(self) -> None:
        self.display_data(simulate_flight(self.clock.elapsed() / 1000))

    def closeEvent(self, event) -> None:
        self.timer.stop()
        super().closeEvent(event)
