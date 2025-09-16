import sys
import random
import psutil
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QBrush
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QFrame, QPushButton, QSizePolicy
)


class CircleIndicator(QWidget):
    """A colored circle indicator for status."""
    def __init__(self, diameter=18, parent=None):
        super().__init__(parent)
        self._color = QColor('gray')
        self._diameter = diameter
        self.setFixedSize(diameter, diameter)

    def setColor(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.NoPen)
        painter.setPen(pen)
        brush = QBrush(self._color)
        painter.setBrush(brush)
        rect = self.rect()
        painter.drawEllipse(rect)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Dashboard")
        self.setWindowIcon(QIcon.fromTheme("applications-system"))
        self.resize(850, 520)

        self.dark_mode = True
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
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Main heading
        heading = QLabel("Real Time Metrics")
        heading.setFont(QFont("Segoe UI", 24, QFont.Bold))
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet("color: #ecf0f1;")
        main_layout.addWidget(heading)

        # Top info panel
        info_panel = QHBoxLayout()
        info_panel.setSpacing(20)

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
        self.plc_indicator = CircleIndicator(18)
        self.plc_status_label = QLabel("Disconnected")
        self.plc_status_label.setFont(QFont("Segoe UI", 14))
        self.plc_status_label.setStyleSheet("color: #e74c3c;")
        plc_status_layout.addWidget(self.plc_indicator)
        plc_status_layout.addSpacing(10)
        plc_status_layout.addWidget(self.plc_status_label)
        plc_status_widget = QWidget()
        plc_status_widget.setLayout(plc_status_layout)
        info_panel.addWidget(self._create_info_box("PLC Connection", plc_status_widget))

        # Light/Dark Mode Toggle Button moved to log section

        main_layout.addLayout(info_panel)

        # Bottom layout: Four parameter frames + Log window
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # Four parameter frames
        params_widget = QWidget()
        params_layout = QGridLayout()
        params_layout.setSpacing(20)

        # Create parameter frames
        self.param_labels = {}

        param_names = ["Temperature (°C)", "Pressure (bar)", "Humidity (%)", "Motor Speed (RPM)"]
        for i, name in enumerate(param_names):
            label_value = QLabel("0")
            label_value.setFont(QFont("Segoe UI", 22, QFont.Bold))
            label_value.setAlignment(Qt.AlignCenter)
            label_value.setStyleSheet("color: #ecf0f1;")
            label_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            frame = self._create_info_box(name, label_value)
            frame.setMinimumSize(180, 110)
            params_layout.addWidget(frame, i // 2, i % 2)
            self.param_labels[name] = label_value

        params_widget.setLayout(params_layout)
        bottom_layout.addWidget(params_widget, 3)

        # Log window
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(10)

        log_title = QLabel("System Log")
        log_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        log_title.setAlignment(Qt.AlignCenter)
        log_layout.addWidget(log_title)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2f;
                color: #ecf0f1;
                font-family: Consolas, monospace;
                font-size: 11pt;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_text)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

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
        bottom_layout.addWidget(log_widget, 2)

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
            self.plc_indicator.setColor("#2ecc71")  # green
            self.plc_status_label.setText("Connected")
            self.plc_status_label.setStyleSheet("color: #2ecc71;")
            self._log("PLC connected.")
        else:
            self.plc_indicator.setColor("#e74c3c")  # red
            self.plc_status_label.setText("Disconnected")
            self.plc_status_label.setStyleSheet("color: #e74c3c;")
            self._log("PLC disconnected.")

    def _update_parameters(self):
        # Simulate real-time parameter updates with random values
        temp = random.uniform(20.0, 80.0)
        pressure = random.uniform(1.0, 10.0)
        humidity = random.uniform(30.0, 90.0)
        motor_speed = random.randint(500, 3000)

        self.param_labels["Temperature (°C)"].setText(f"{temp:.1f}")
        self.param_labels["Pressure (bar)"].setText(f"{pressure:.2f}")
        self.param_labels["Humidity (%)"].setText(f"{humidity:.1f}")
        self.param_labels["Motor Speed (RPM)"].setText(f"{motor_speed}")

        self._log(f"Parameters updated: Temp={temp:.1f}°C, Pressure={pressure:.2f} bar, "
                  f"Humidity={humidity:.1f}%, Motor Speed={motor_speed} RPM")

    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def _create_info_box(self, title, widget):
        box = QFrame()
        box.setFrameShape(QFrame.StyledPanel)
        box.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        layout = QVBoxLayout()
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        label.setStyleSheet("color: #ecf0f1;")
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
                    background-color: #2980b9;
                    border: none;
                    color: white;
                    padding: 7px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
                QTextEdit {
                    background-color: #1e1e2f;
                    color: #ecf0f1;
                    font-family: Consolas, monospace;
                    font-size: 11pt;
                    border-radius: 8px;
                    padding: 8px;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #f0f0f0;
                    color: #2c3e50;
                    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                }
                QLabel {
                    color: #2c3e50;
                }
                QPushButton {
                    background-color: #2980b9;
                    border: none;
                    color: white;
                    padding: 7px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #2c3e50;
                    font-family: Consolas, monospace;
                    font-size: 11pt;
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame {
                    background-color: #dfe6e9;
                    border-radius: 10px;
                    padding: 14px;
                }
            """

    def _toggle_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.mode_toggle_btn.setText("Switch to Light Mode")
        else:
            self.mode_toggle_btn.setText("Switch to Dark Mode")
        self.setStyleSheet(self._get_stylesheet())
        # Also update frames background colors for light mode
        for frame in self.findChildren(QFrame):
            if self.dark_mode:
                frame.setStyleSheet("""
                    QFrame {
                        background-color: #2c3e50;
                        border-radius: 10px;
                        padding: 5px;
                    }
                """)
            else:
                frame.setStyleSheet("""
                    QFrame {
                        background-color: #dfe6e9;
                        border-radius: 10px;
                        padding: 5px;
                    }
                """)


def main():
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
