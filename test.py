import sys
import random
import psutil
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QBrush, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QFrame, QPushButton, QSizePolicy
)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Dashboard")
        self.setWindowIcon(QIcon.fromTheme("applications-system"))
        self.resize(850, 520)

        self.dark_mode = False
        self.setStyleSheet(self._get_stylesheet())

        self.last_backup_time = datetime.now() - timedelta(hours=2, minutes=15)
        self.plc_connected = False

        # Store original window size for scaling
        self.original_size = (850, 520)
        self.original_fonts = {
            'heading': 24,
            'time': 22,
            'backup': 14,
            'plc': 14,
            'log_title': 18,
            'param_title': 12,
            'param_value': 22,
            'button': 10
        }

        self._init_ui()
        self._init_timers()
        self._log("Dashboard initialized.")

    def _init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top header with logo and heading
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setAlignment(Qt.AlignLeft)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("logo.PNG")
        logo_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio))
        header_layout.addWidget(logo_label)

        # Right side: main heading and subheading
        right_layout = QVBoxLayout()
        right_layout.setSpacing(2)

        # Main heading
        heading = QLabel("Production Analyser")
        heading.setFont(QFont("Segoe UI", 20, QFont.Bold))
        heading.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(heading)

        # Subheading
        subheading = QLabel("Real Time Metrics")
        subheading.setFont(QFont("Segoe UI", 10))
        subheading.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(subheading)

        header_layout.addLayout(right_layout)

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Top info panel
        info_panel = QHBoxLayout()
        info_panel.setSpacing(15)

        # O.E.E (%)
        self.oee_label = QLabel("0.0")
        self.oee_label.setFont(QFont("Segoe UI", 15))
        self.oee_label.setAlignment(Qt.AlignCenter)
        self.oee_label.setFixedWidth(220)
        oee_box = self._create_info_box("O.E.E (%)", self.oee_label)
        oee_box.setFixedWidth(250)
        info_panel.addWidget(oee_box)

        # Current Time
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFixedWidth(220)
        time_box = self._create_info_box("Current Time", self.time_label)
        time_box.setFixedWidth(250)
        info_panel.addWidget(time_box)

        # Last Backup Time
        self.backup_label = QLabel()
        self.backup_label.setFont(QFont("Segoe UI", 15))
        self.backup_label.setAlignment(Qt.AlignCenter)
        self.backup_label.setFixedWidth(220)
        backup_box = self._create_info_box("Last Backup", self.backup_label)
        backup_box.setFixedWidth(250)
        info_panel.addWidget(backup_box)

        # PLC Connection Status
        plc_status_layout = QHBoxLayout()
        plc_status_layout.setAlignment(Qt.AlignCenter)
        self.plc_status_label = QLabel("Disconnected")
        self.plc_status_label.setFont(QFont("Segoe UI", 14))
        self.plc_status_label.setStyleSheet("color: white; background-color: #FF0000; border-radius: 0px; padding: 4px 8px;")
        plc_status_layout.addWidget(self.plc_status_label)
        plc_status_widget = QWidget()
        plc_status_widget.setLayout(plc_status_layout)
        info_panel.addWidget(self._create_info_box("PLC Connection", plc_status_widget))

        # Light/Dark Mode Toggle Button moved to log section

        main_layout.addLayout(info_panel)

        # Bottom layout: Four parameter frames + Log window
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(15)

        # Four parameter frames
        params_widget = QWidget()
        params_layout = QGridLayout()
        params_layout.setSpacing(15)

        # Create parameter frames
        self.param_labels = {}

        param_names = ["Total Delay (in mins)", "Total Production (in units)", "Shift A Production (in units)", "Shift B Production (in units)"]
        for i, name in enumerate(param_names):
            label_value = QLabel("0")
            label_value.setFont(QFont("Segoe UI", 22, QFont.Bold))
            label_value.setAlignment(Qt.AlignCenter)
            label_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            frame = self._create_info_box(name, label_value)
            frame.setMinimumSize(180, 110)
            params_layout.addWidget(frame, i // 2, i % 2)
            self.param_labels[name] = label_value

        params_widget.setLayout(params_layout)
        bottom_layout.addWidget(params_widget)

        # Log window
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(5)

        log_title = QLabel("Events")
        log_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        log_title.setAlignment(Qt.AlignLeft)
        log_layout.addWidget(log_title)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)

        # Add a clear log button
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.setFixedWidth(100)
        clear_log_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        clear_log_btn.clicked.connect(self.log_text.clear)
        buttons_layout.addWidget(clear_log_btn)

        # Light/Dark Mode Toggle Button moved here for smoother functioning
        self.mode_toggle_btn = QPushButton("Switch to Light Mode")
        self.mode_toggle_btn.setFixedSize(180, 36)
        self.mode_toggle_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.mode_toggle_btn.clicked.connect(self._toggle_mode)
        buttons_layout.addWidget(self.mode_toggle_btn)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        log_layout.addWidget(buttons_widget, alignment=Qt.AlignRight)

        log_widget.setLayout(log_layout)
        bottom_layout.addWidget(log_widget)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def _init_timers(self):
        # Update current time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()

        # Update backup time every minute (simulate)
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self._update_backup_time)
        self.backup_timer.start(60000)
        self._update_backup_time()

        # Update PLC connection status every 5 seconds (simulate)
        self.plc_timer = QTimer()
        self.plc_timer.timeout.connect(self._update_plc_status)
        self.plc_timer.start(5000)
        self._update_plc_status()

        # Update parameters every second
        self.params_timer = QTimer()
        self.params_timer.timeout.connect(self._update_parameters)
        self.params_timer.start(1000)
        self._update_parameters()

    def _update_time(self):
        now = QTime.currentTime()
        self.time_label.setText(now.toString("hh:mm:ss AP"))
        # Log every minute
        if now.second() == 0:
            self._log(f"Time updated: {now.toString('hh:mm:ss AP')}")

    def _update_backup_time(self):
        elapsed = datetime.now() - self.last_backup_time
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        self.backup_label.setText(f"{hours}h {minutes}m ago")

    def _update_plc_status(self):
        self.plc_connected = not self.plc_connected
        if self.plc_connected:
            self.plc_status_label.setText("Connected")
            self.plc_status_label.setStyleSheet("color: white; background-color: #008000; border-radius: 0px; padding: 4px 8px;")
            self._log("PLC connected.")
        else:
            self.plc_status_label.setText("Disconnected")
            self.plc_status_label.setStyleSheet("color: white; background-color: #FF0000; border-radius: 0px; padding: 4px 8px;")
            self._log("PLC disconnected.")

    def _update_parameters(self):
        # Simulate real-time parameter updates with random values
        delay = random.uniform(0, 100)
        total_prod = random.randint(100, 1000)
        shift_a = random.randint(50, 500)
        shift_b = random.randint(50, 500)
        oee = random.uniform(50.0, 100.0)

        self.param_labels["Total Delay (in mins)"].setText(f"{delay:.1f}")
        self.param_labels["Total Production (in units)"].setText(f"{total_prod}")
        self.param_labels["Shift A Production (in units)"].setText(f"{shift_a}")
        self.param_labels["Shift B Production (in units)"].setText(f"{shift_b}")
        self.oee_label.setText(f"{oee:.1f}")

        self._log(f"Parameters updated: Delay={delay:.1f} mins, Total Prod={total_prod} units, "
                  f"Shift A={shift_a} units, Shift B={shift_b} units, O.E.E={oee:.1f}%")

    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def _create_info_box(self, title, widget):
        box = QFrame()
        box.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(widget)
        box.setLayout(layout)
        return box


    def _get_stylesheet(self):
        if self.dark_mode:
            return """
                QWidget {
                    background-color: #34495e;
                    color: #ecf0f1;
                    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                }
                QLabel {
                    color: #ecf0f1;
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
                QTextEdit {
                    background-color: #1e1e2f;
                    color: #ecf0f1;
                    font-family: Consolas, monospace;
                    font-size: 11pt;
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame {
                    background-color: #2c3e50;
                    border-radius: 10px;
                    padding: 3px;
                }
            """
        else:
            return """
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
                QTextEdit {
                    background-color: #ffffff;
                    color: #002A4D;
                    font-family: Consolas, monospace;
                    font-size: 11pt;
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame {
                    background-color: #C6E5F5;
                    border-radius: 10px;
                    padding: 5px;
                }
            """

    def _toggle_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.mode_toggle_btn.setText("Switch to Light Mode")
        else:
            self.mode_toggle_btn.setText("Switch to Dark Mode")
        self.setStyleSheet(self._get_stylesheet())


def main():
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
