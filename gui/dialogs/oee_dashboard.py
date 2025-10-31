import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QFormLayout, QLineEdit, QDesktopWidget
)
from PyQt5.QtCore import QTime, QTimer, Qt
from PyQt5.QtGui import QFont, QIcon

from plc.oee_calculator import OEECalculator
from gui.dialogs.oee_config_dialog import ConfigDialog

class OEEDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detailed OEE Information - Production Analyser")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedSize(400, 400)
        self.center()
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                color: #002A4D;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            }
            QLabel {
                color: #002A4D;
            }
            QPushButton {
                background-color: #002A4D;
                border: none;
                color: white;
                padding: 7px 14px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003A5D;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #002A4D;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        # Initialize calculator
        self.calc = OEECalculator()

        # Start realtime calculation thread
        self.calc.start_realtime_calculation()

        # Current shift (simulate shift A for testing)
        now = datetime.now()
        self.shift_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        self.shift_end = now.replace(hour=16, minute=0, second=0, microsecond=0)

        self.init_ui()

        # Timer for realtime updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_oee)
        self.timer.start(2000)  # Update every 2 seconds to match calculation thread

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # OEE Metrics Group
        oee_group = QGroupBox("Current OEE Metrics")
        oee_layout = QFormLayout()
        oee_layout.setSpacing(10)
        oee_layout.setContentsMargins(15, 15, 15, 15)

        self.lbl_availability = QLabel("0.00%")
        self.lbl_performance = QLabel("0.00%")
        self.lbl_quality = QLabel("0.00%")
        self.lbl_oee = QLabel("0.00%")

        oee_layout.addRow("Availability:", self.lbl_availability)
        oee_layout.addRow("Performance:", self.lbl_performance)
        oee_layout.addRow("Quality:", self.lbl_quality)
        oee_layout.addRow("Overall OEE:", self.lbl_oee)

        oee_group.setLayout(oee_layout)
        layout.addWidget(oee_group)

        # Production Data Group
        prod_group = QGroupBox("Production Data")
        prod_layout = QFormLayout()
        prod_layout.setSpacing(10)
        prod_layout.setContentsMargins(15, 15, 15, 15)

        self.lbl_total_count = QLabel("0")
        self.lbl_good_count = QLabel("0")
        self.lbl_downtime = QLabel("0.0 min")
        self.lbl_elapsed_time = QLabel("0 min")

        prod_layout.addRow("Total Count:", self.lbl_total_count)
        prod_layout.addRow("Good Count:", self.lbl_good_count)
        prod_layout.addRow("Downtime:", self.lbl_downtime)
        prod_layout.addRow("Elapsed Time (excl. breaks):", self.lbl_elapsed_time)

        prod_group.setLayout(prod_layout)
        layout.addWidget(prod_group)

        # Config button at the bottom
        config_layout = QHBoxLayout()
        config_btn = QPushButton("Open OEE Configuration")
        config_btn.clicked.connect(self.open_config)
        config_layout.addWidget(config_btn)
        config_layout.addStretch()
        layout.addLayout(config_layout)

    def open_config(self):
        dialog = ConfigDialog()
        dialog.exec_()
        # Reload config after dialog closes
        self.calc = OEECalculator()

    def update_oee(self):
        current_time = datetime.now()

        # Get latest OEE data from realtime calculation
        oee_data = self.calc.get_latest_oee()

        # Get current production data from realtime calculation
        total_pieces, current_downtime = self.calc.get_current_production_data()

        # Update production labels with realtime data
        self.lbl_total_count.setText(str(total_pieces))
        self.lbl_good_count.setText(str(total_pieces))  # Assuming all are good for now
        self.lbl_downtime.setText(f"{current_downtime:.1f} min")

        # Calculate elapsed time
        breaks = self.calc.get_breaks()
        elapsed = self.calc.calculate_elapsed_minutes(self.shift_start, self.shift_end, current_time, breaks)
        self.lbl_elapsed_time.setText(f"{elapsed} min")

        # Update OEE labels with realtime data
        self.lbl_availability.setText(f"{oee_data['availability']:.2f}%")
        self.lbl_performance.setText(f"{oee_data['performance']:.2f}%")
        self.lbl_quality.setText(f"{oee_data['quality']:.2f}%")
        self.lbl_oee.setText(f"{oee_data['oee']:.2f}%")

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = OEEDashboard()
    dashboard.show()
    sys.exit(app.exec_())
