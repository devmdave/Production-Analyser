import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTimeEdit, QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt5.QtCore import QTime

class ConfigDialog(QDialog):
    def __init__(self, config_file="oee_config.json", parent=None):
        super().__init__(parent)
        self.config_file = config_file
        self.setWindowTitle("OEE Configuration")
        self.setFixedSize(400, 500)
        self.layout = QVBoxLayout(self)

        # Load existing config if available
        self.config = self.load_config()

        # Form layout for inputs
        form_layout = QFormLayout()

        # Shift A
        self.shift_a_start = QTimeEdit()
        self.shift_a_start.setDisplayFormat("HH:mm")
        self.shift_a_start.setTime(QTime.fromString(self.config.get("shift_a_start", "08:00"), "HH:mm"))
        form_layout.addRow("Shift A Start Time:", self.shift_a_start)

        self.shift_a_end = QTimeEdit()
        self.shift_a_end.setDisplayFormat("HH:mm")
        self.shift_a_end.setTime(QTime.fromString(self.config.get("shift_a_end", "16:00"), "HH:mm"))
        form_layout.addRow("Shift A End Time:", self.shift_a_end)

        # Shift B
        self.shift_b_start = QTimeEdit()
        self.shift_b_start.setDisplayFormat("HH:mm")
        self.shift_b_start.setTime(QTime.fromString(self.config.get("shift_b_start", "16:00"), "HH:mm"))
        form_layout.addRow("Shift B Start Time:", self.shift_b_start)

        self.shift_b_end = QTimeEdit()
        self.shift_b_end.setDisplayFormat("HH:mm")
        self.shift_b_end.setTime(QTime.fromString(self.config.get("shift_b_end", "00:00"), "HH:mm"))
        form_layout.addRow("Shift B End Time:", self.shift_b_end)

        # Shift C
        self.shift_c_start = QTimeEdit()
        self.shift_c_start.setDisplayFormat("HH:mm")
        self.shift_c_start.setTime(QTime.fromString(self.config.get("shift_c_start", "00:00"), "HH:mm"))
        form_layout.addRow("Shift C Start Time:", self.shift_c_start)

        self.shift_c_end = QTimeEdit()
        self.shift_c_end.setDisplayFormat("HH:mm")
        self.shift_c_end.setTime(QTime.fromString(self.config.get("shift_c_end", "08:00"), "HH:mm"))
        form_layout.addRow("Shift C End Time:", self.shift_c_end)

        # Ideal Cycle Time
        self.ideal_cycle_time = QLineEdit(self.config.get("ideal_cycle_time", "1.0"))
        form_layout.addRow("Ideal Cycle Time (minutes):", self.ideal_cycle_time)

        # Current Production Units Tag
        self.production_tag = QLineEdit(self.config.get("production_tag", ""))
        form_layout.addRow("Production Units Tag:", self.production_tag)

        # Current Total Fault Delay Tag
        self.fault_delay_tag = QLineEdit(self.config.get("fault_delay_tag", ""))
        form_layout.addRow("Total Fault Delay Tag:", self.fault_delay_tag)

        self.layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_config)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {}

    def save_config(self):
        config = {
            "shift_a_start": self.shift_a_start.time().toString("HH:mm"),
            "shift_a_end": self.shift_a_end.time().toString("HH:mm"),
            "shift_b_start": self.shift_b_start.time().toString("HH:mm"),
            "shift_b_end": self.shift_b_end.time().toString("HH:mm"),
            "shift_c_start": self.shift_c_start.time().toString("HH:mm"),
            "shift_c_end": self.shift_c_end.time().toString("HH:mm"),
            "ideal_cycle_time": self.ideal_cycle_time.text(),
            "production_tag": self.production_tag.text(),
            "fault_delay_tag": self.fault_delay_tag.text()
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

    def accept_config(self):
        # Validate inputs
        try:
            float(self.ideal_cycle_time.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Ideal Cycle Time must be a number.")
            return

        if not self.production_tag.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Production Units Tag is required.")
            return

        if not self.fault_delay_tag.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Total Fault Delay Tag is required.")
            return

        self.save_config()
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    dialog.exec_()
    sys.exit(app.exec_())
