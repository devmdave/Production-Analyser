import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTimeEdit, QDialogButtonBox, QFormLayout, QMessageBox,
    QGroupBox, QSpacerItem, QSizePolicy, QTabWidget, QWidget, QDesktopWidget
)
from PyQt5.QtCore import QTime

class ConfigDialog(QDialog):
    def __init__(self, config_file="oee_config.json", parent=None):
        super().__init__(parent)
        self.config_file = config_file
        self.setWindowTitle("OEE Configuration")
        self.setFixedSize(600, 500)
        self.center()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
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
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #003A5D;
            }
            QPushButton:pressed {
                background-color: #001A2D;
            }
            QLineEdit {
                border: 1px solid #002A4D;
                border-radius: 4px;
                padding: 5px;
            }
            QTimeEdit {
                border: 1px solid #002A4D;
                border-radius: 4px;
                padding: 5px;
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
            QTabWidget::pane {
                border: 1px solid #002A4D;
            }
            QTabBar::tab {
                background: #C6E5F5;
                border: 1px solid #002A4D;
                padding: 8px;
                color: #002A4D;
            }
            QTabBar::tab:selected {
                background: #AAD8F0;
            }
        """)

        # Load existing config if available
        self.config = self.load_config()

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Shifts Tab
        shifts_tab = QWidget()
        shifts_layout = QVBoxLayout(shifts_tab)

        # Group shifts
        shift_group = QGroupBox("Shift Configurations")
        shift_layout = QFormLayout()

        # Shift A
        self.shift_a_start = QTimeEdit()
        self.shift_a_start.setDisplayFormat("HH:mm")
        self.shift_a_start.setTime(QTime.fromString(self.config.get("shift_a_start", "08:00"), "HH:mm"))
        shift_layout.addRow("Shift A Start Time:", self.shift_a_start)

        self.shift_a_end = QTimeEdit()
        self.shift_a_end.setDisplayFormat("HH:mm")
        self.shift_a_end.setTime(QTime.fromString(self.config.get("shift_a_end", "16:00"), "HH:mm"))
        shift_layout.addRow("Shift A End Time:", self.shift_a_end)

        # Shift B
        self.shift_b_start = QTimeEdit()
        self.shift_b_start.setDisplayFormat("HH:mm")
        self.shift_b_start.setTime(QTime.fromString(self.config.get("shift_b_start", "16:00"), "HH:mm"))
        shift_layout.addRow("Shift B Start Time:", self.shift_b_start)

        self.shift_b_end = QTimeEdit()
        self.shift_b_end.setDisplayFormat("HH:mm")
        self.shift_b_end.setTime(QTime.fromString(self.config.get("shift_b_end", "00:00"), "HH:mm"))
        shift_layout.addRow("Shift B End Time:", self.shift_b_end)

        # Shift C
        self.shift_c_start = QTimeEdit()
        self.shift_c_start.setDisplayFormat("HH:mm")
        self.shift_c_start.setTime(QTime.fromString(self.config.get("shift_c_start", "00:00"), "HH:mm"))
        shift_layout.addRow("Shift C Start Time:", self.shift_c_start)

        self.shift_c_end = QTimeEdit()
        self.shift_c_end.setDisplayFormat("HH:mm")
        self.shift_c_end.setTime(QTime.fromString(self.config.get("shift_c_end", "08:00"), "HH:mm"))
        shift_layout.addRow("Shift C End Time:", self.shift_c_end)

        shift_group.setLayout(shift_layout)
        shifts_layout.addWidget(shift_group)
        self.tab_widget.addTab(shifts_tab, "Shifts")

        # Production Tab
        prod_tab = QWidget()
        prod_layout = QVBoxLayout(prod_tab)

        # Group production settings
        prod_group = QGroupBox("Production Settings")
        prod_form_layout = QFormLayout()

        # PLC IP Address
        self.plc_ip = QLineEdit(self.config.get("plc_ip", ""))
        prod_form_layout.addRow("PLC IP Address:", self.plc_ip)

        # Ideal Cycle Time
        self.ideal_cycle_time = QLineEdit(self.config.get("ideal_cycle_time", "1.0"))
        prod_form_layout.addRow("Ideal Cycle Time (minutes):", self.ideal_cycle_time)

        # Current Production Units Tag
        self.production_tag = QLineEdit(self.config.get("production_tag", ""))
        prod_form_layout.addRow("Production Units Tag:", self.production_tag)

        # Current Total Fault Delay Tag
        self.fault_delay_tag = QLineEdit(self.config.get("fault_delay_tag", ""))
        prod_form_layout.addRow("Total Fault Delay Tag:", self.fault_delay_tag)

        prod_group.setLayout(prod_form_layout)
        prod_layout.addWidget(prod_group)
        self.tab_widget.addTab(prod_tab, "Production")

        # Breaks Tab
        breaks_tab = QWidget()
        breaks_layout = QVBoxLayout(breaks_tab)

        # Group breaks
        breaks_group = QGroupBox("Break Configurations")
        breaks_form_layout = QFormLayout()

        # Break 1
        self.break_1_start = QTimeEdit()
        self.break_1_start.setDisplayFormat("HH:mm")
        self.break_1_start.setTime(QTime.fromString(self.config.get("break_1_start", "10:00"), "HH:mm"))
        breaks_form_layout.addRow("Break 1 Start Time:", self.break_1_start)

        self.break_1_end = QTimeEdit()
        self.break_1_end.setDisplayFormat("HH:mm")
        self.break_1_end.setTime(QTime.fromString(self.config.get("break_1_end", "10:15"), "HH:mm"))
        breaks_form_layout.addRow("Break 1 End Time:", self.break_1_end)

        # Break 2
        self.break_2_start = QTimeEdit()
        self.break_2_start.setDisplayFormat("HH:mm")
        self.break_2_start.setTime(QTime.fromString(self.config.get("break_2_start", "14:00"), "HH:mm"))
        breaks_form_layout.addRow("Break 2 Start Time:", self.break_2_start)

        self.break_2_end = QTimeEdit()
        self.break_2_end.setDisplayFormat("HH:mm")
        self.break_2_end.setTime(QTime.fromString(self.config.get("break_2_end", "14:15"), "HH:mm"))
        breaks_form_layout.addRow("Break 2 End Time:", self.break_2_end)

        # Break 3
        self.break_3_start = QTimeEdit()
        self.break_3_start.setDisplayFormat("HH:mm")
        self.break_3_start.setTime(QTime.fromString(self.config.get("break_3_start", "16:00"), "HH:mm"))
        breaks_form_layout.addRow("Break 3 Start Time:", self.break_3_start)

        self.break_3_end = QTimeEdit()
        self.break_3_end.setDisplayFormat("HH:mm")
        self.break_3_end.setTime(QTime.fromString(self.config.get("break_3_end", "16:15"), "HH:mm"))
        breaks_form_layout.addRow("Break 3 End Time:", self.break_3_end)

        breaks_group.setLayout(breaks_form_layout)
        breaks_layout.addWidget(breaks_group)
        self.tab_widget.addTab(breaks_tab, "Breaks")

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
            "plc_ip": self.plc_ip.text(),
            "ideal_cycle_time": self.ideal_cycle_time.text(),
            "production_tag": self.production_tag.text(),
            "fault_delay_tag": self.fault_delay_tag.text(),
            "break_1_start": self.break_1_start.time().toString("HH:mm"),
            "break_1_end": self.break_1_end.time().toString("HH:mm"),
            "break_2_start": self.break_2_start.time().toString("HH:mm"),
            "break_2_end": self.break_2_end.time().toString("HH:mm"),
            "break_3_start": self.break_3_start.time().toString("HH:mm"),
            "break_3_end": self.break_3_end.time().toString("HH:mm")
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

        if not self.plc_ip.text().strip():
            QMessageBox.warning(self, "Invalid Input", "PLC IP Address is required.")
            return

        self.save_config()
        self.accept()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    dialog.exec_()
    sys.exit(app.exec_())
