"""Run the original telemetry demo, or opt into the independent HUD."""
import argparse
import sys

from PySide6.QtWidgets import QApplication

from wardog.ui.window import FlightWindow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WarDog desktop prototypes")
    parser.add_argument("--hud", action="store_true", help="start marker-only overlay")
    parser.add_argument("--calibrate", action="store_true", help="start HUD with calibration controls")
    args = parser.parse_args([] if argv is None else argv)
    app = QApplication(sys.argv)
    app.setOrganizationName("WarDog")
    app.setApplicationName("WarDog")
    if args.hud or args.calibrate:
        from wardog.hud.application import HudController
        controller = HudController(app, calibrate=args.calibrate)
        try:
            return app.exec()
        finally:
            controller.close_windows()
    window = FlightWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
