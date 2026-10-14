"""Run with python -m wardog from the repository root."""
import sys

from PySide6.QtWidgets import QApplication

from wardog.ui.window import FlightWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = FlightWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
