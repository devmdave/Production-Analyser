import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QFrame,
                             QFormLayout, QTimeEdit, QDialog, QDialogButtonBox, QListWidget)
from PyQt5.QtCore import Qt, QTimer, QTime, QSize
from PyQt5.QtGui import QFont

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dash Board")
        self.resize(800, 600)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Title label at top center with bold font
        title_label = QLabel("Dash Board", self)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)  # Center align text:contentReference[oaicite:0]{index=0}
        main_layout.addWidget(title_label)

        # Grid layout for the 4 frames (2x2)
        grid = QGridLayout()
        grid.setSpacing(10)
        main_layout.addLayout(grid)

        # Top-Left Frame: Parameters (placeholder content)
        top_left_frame = QFrame(self)
        top_left_frame.setFrameShape(QFrame.StyledPanel)
        top_left_layout = QFormLayout(top_left_frame)
        top_left_layout.addRow("Parameter 1:", QLabel("Value 1"))
        top_left_layout.addRow("Parameter 2:", QLabel("Value 2"))
        top_left_layout.addRow("Parameter 3:", QLabel("Value 3"))
        top_left_layout.addRow("Parameter 4:", QLabel("Value 4"))

        # Top-Right Frame: PLC Communication data (placeholder)
        top_right_frame = QFrame(self)
        top_right_frame.setFrameShape(QFrame.StyledPanel)
        top_right_layout = QFormLayout(top_right_frame)
        top_right_layout.addRow("PLC Status:", QLabel("Connected"))
        top_right_layout.addRow("Last Read Time:", QLabel("10:00:00"))
        top_right_layout.addRow("PLC Data:", QLabel("1234"))
        top_right_layout.addRow("Alarm:", QLabel("None"))

        # Bottom-Left Frame: System time and backup timing
        bottom_left_frame = QFrame(self)
        bottom_left_frame.setFrameShape(QFrame.StyledPanel)
        bottom_left_layout = QVBoxLayout(bottom_left_frame)
        bottom_left_layout.setAlignment(Qt.AlignTop)

        # Label for current system time
        self.current_time_label = QLabel(self)
        font = QFont()
        font.setPointSize(12)
        self.current_time_label.setFont(font)
        bottom_left_layout.addWidget(self.current_time_label)

        # Label for backup timing
        self.backup_time_label = QLabel("Backup Time: --:--:--", self)
        self.backup_time_label.setFont(font)
        bottom_left_layout.addWidget(self.backup_time_label)

        # Button to set new backup time
        backup_btn = QPushButton("Set New Backup Time", self)
        bottom_left_layout.addWidget(backup_btn)

        # Bottom-Right Frame: List of recent backup data files
        bottom_right_frame = QFrame(self)
        bottom_right_frame.setFrameShape(QFrame.StyledPanel)
        bottom_right_layout = QVBoxLayout(bottom_right_frame)
        bottom_right_layout.setAlignment(Qt.AlignTop)

        recent_label = QLabel("Recent Backups:")
        recent_label.setFont(font)
        bottom_right_layout.addWidget(recent_label)
        self.backup_list = QListWidget(self)
        # Add mock backup file names to list
        self.backup_list.addItems([
            "backup_2025-09-15_10-00.log",
            "backup_2025-09-15_09-00.log",
            "backup_2025-09-15_08-00.log",
            "backup_2025-09-15_07-00.log"
        ])
        bottom_right_layout.addWidget(self.backup_list)

        # Add frames to grid layout (2x2)
        grid.addWidget(top_left_frame, 0, 0)
        grid.addWidget(top_right_frame, 0, 1)
        grid.addWidget(bottom_left_frame, 1, 0)
        grid.addWidget(bottom_right_frame, 1, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)  # Equal stretch so each frame resizes evenly:contentReference[oaicite:1]{index=1}

        # Timer to update the current time label every second:contentReference[oaicite:2]{index=2}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1000ms = 1s

        # Connect button to slot for setting new backup time
        backup_btn.clicked.connect(self.set_backup_time)

        # Initialize current time label text
        self.update_time()

    def update_time(self):
        """Update the current system time label"""
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.current_time_label.setText(f"Current Time: {current_time}")

    def set_backup_time(self):
        """Open a dialog to set a new backup time"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Set New Backup Time")
        dialog_layout = QVBoxLayout(dialog)

        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm:ss")
        dialog_layout.addWidget(time_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialog_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            new_time = time_edit.time().toString("HH:mm:ss")
            self.backup_time_label.setText(f"Backup Time: {new_time}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())
