import sys
import argparse
from PyQt5.QtWidgets import QApplication
from gui.dashboard import Dashboard


def main():
    parser = argparse.ArgumentParser(description="Run test.py with plc or no-plc mode")
    parser.add_argument("mode", choices=["plc", "no-plc"], default="no-plc", help="Choose 'plc' or 'no-plc' mode")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    dashboard = Dashboard(args.mode)

    dashboard.show()
    sys.exit(app.exec_())
    


if __name__ == "__main__":
    main()
