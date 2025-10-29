import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QFormLayout, QLineEdit
)
from PyQt5.QtCore import QTime, QTimer, Qt
from PyQt5.QtGui import QFont

from oee_calculator import OEECalculator
from OEE_config_dialog import ConfigDialog

class OEEDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OEE Dashboard - Testing")
        self.setGeometry(100, 100, 600, 400)

        # Initialize calculator
        self.calc = OEECalculator()

        # Simulated production data
        self.total_count = 0
        self.good_count = 0
        self.downtime = 0.0

        # Current shift (simulate shift A for testing)
        now = datetime.now()
        self.shift_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        self.shift_end = now.replace(hour=16, minute=0, second=0, microsecond=0)

        self.init_ui()

        # Timer for realtime updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_oee)
        self.timer.start(5000)  # Update every 5 seconds

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("OEE Realtime Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Config button
        config_layout = QHBoxLayout()
        config_btn = QPushButton("Open OEE Configuration")
        config_btn.clicked.connect(self.open_config)
        config_layout.addWidget(config_btn)
        config_layout.addStretch()
        layout.addLayout(config_layout)

        # OEE Metrics Group
        oee_group = QGroupBox("Current OEE Metrics")
        oee_layout = QFormLayout()

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
        prod_group = QGroupBox("Production Data (Simulated)")
        prod_layout = QFormLayout()

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

        # Simulate production button
        simulate_btn = QPushButton("Simulate Production Update")
        simulate_btn.clicked.connect(self.simulate_production)
        layout.addWidget(simulate_btn)

    def open_config(self):
        dialog = ConfigDialog()
        dialog.exec_()
        # Reload config after dialog closes
        self.calc = OEECalculator()

    def simulate_production(self):
        # Simulate adding production data
        import random
        add_total = random.randint(120, 127)
        add_good = random.randint(110, add_total)
        add_downtime = random.uniform(0, 1)

        self.total_count += add_total
        self.good_count += add_good
        self.downtime += add_downtime

    def update_oee(self):
        current_time = datetime.now()

        # Update production labels
        self.lbl_total_count.setText(str(self.total_count))
        self.lbl_good_count.setText(str(self.good_count))
        self.lbl_downtime.setText(f"{self.downtime:.1f} min")

        # Calculate elapsed time
        breaks = self.calc.get_breaks()
        elapsed = self.calc.calculate_elapsed_minutes(self.shift_start, self.shift_end, current_time, breaks)
        self.lbl_elapsed_time.setText(f"{elapsed} min")

        # Calculate OEE
        oee_data = self.calc.compute_realtime_oee(
            self.shift_start, self.shift_end, current_time,
            self.total_count, self.good_count, self.downtime
        )

        # Update OEE labels
        self.lbl_availability.setText(f"{oee_data['availability']:.2f}%")
        self.lbl_performance.setText(f"{oee_data['performance']:.2f}%")
        self.lbl_quality.setText(f"{oee_data['quality']:.2f}%")
        self.lbl_oee.setText(f"{oee_data['oee']:.2f}%")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = OEEDashboard()
    dashboard.show()
    sys.exit(app.exec_())
