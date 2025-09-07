from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QStatusBar
from PyQt5.QtCore import QTimer
import sys

class StatusBar():
    def __init__(self,layout):
        super().__init__()

        # Create and set status bar
        self.status_bar = QStatusBar()
        layout.setStatusBar(self.status_bar)

        # Simulate error
        self.show_error("PLC connection failed!")

    def show_error(self, message):
        self.status_bar.setStyleSheet("color: white; background-color: red;")
        self.status_bar.showMessage(message)
        # Auto-dismiss after 5 seconds
        QTimer.singleShot(5000, self.clear_status)

    def clear_status(self):
        self.status_bar.clearMessage()
        self.status_bar.setStyleSheet("")  # Reset style
