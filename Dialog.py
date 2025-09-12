import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
import os
import subprocess
import signal
from PyQt5.QtWidgets import QDialog, QVBoxLayout,QTimeEdit, QListView, QPushButton, QHBoxLayout, QLabel, QDialogButtonBox,QProgressDialog
from PyQt5.QtCore import QStringListModel, Qt,QTime

class BackupTimeDialog(QDialog):
    def __init__(self, current_time=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Backup Time")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        self.status = False

        label = QLabel("Select new backup time:")
        layout.addWidget(label)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        if current_time:
            self.time_edit.setTime(current_time)
        else:
            self.time_edit.setTime(QTime.currentTime())
        layout.addWidget(self.time_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.get_time)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def show(self):
        self.exec_()

    def get_time(self):
        f = lambda : (self.time_edit.time().toString("HH:mm"), self.destroy())
        running_pid = os.getenv("PRODUCTION_BACKUP_PID")
        if running_pid:
            os.kill(running_pid, signal.SIGTERM)
        # Start the .exe and get the process object
        args = [f"{f()[0]}"]
        print(args)
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(
            [f"write_at_time.exe"]+args,
            creationflags=DETACHED_PROCESS
        )

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Automated Production Analyser")
        msg.setText(f"We have saved your time. \n Backup will be stored at {f()[0]}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

class CustomListViewDialog(QDialog):
    def __init__(self, items, title="Select an Item", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)
        self.selected_item = None

        layout = QVBoxLayout(self)

        label = QLabel("Please select an item:")
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label)

        self.list_view = QListView()
        self.model = QStringListModel(items)
        self.list_view.setModel(self.model)
        layout.addWidget(self.list_view)

        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.exec_()

    def accept_selection(self):
        selected = self.list_view.selectedIndexes()
        if selected:
            self.selected_item = self.model.data(selected[0], Qt.DisplayRole)
            self.accept()
        else:
            self.selected_item = None
            self.reject()
        return selected[0].data()

class Dialog:
    def __init__(self):
        pass
    def show_file_not_found_error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Automated Production Analyser")
        msg.setText("Sorry, We are unable to load the data at this moment.\n")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    def show_success_data_loaded(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Automated Production Analyser")
        msg.setText("Data Loaded Successfully!")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    def show_no_tags_error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Automated Production Analyser")
        msg.setText("There are no tags created currently!\nThis can lead to empty excel file or no data.\nPlease create tags using edit tags option.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    def show_error_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Automated Production Analyser")
        msg.setText("No previous records found. \n We do not have any backup data at this moment.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    def show_plc_connection_error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Connection Error")
        msg.setText("Plc Connection Failed. \n Please check your PLC connection and try again.")
        msg.setStandardButtons(QMessageBox.Ok)

        # 🔴 Red-themed styling
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffdddd;
                font-size: 14px;
            }
            QLabel {
                color: #b00000;
                font-weight: bold;
            }
            QPushButton {
                background-color: #b00000;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d00000;
            }
        """)

        msg.exec_()
    def show_progress_dialog(self):
        self.dialog = QProgressDialog("PLease Wait while we are loading PLC Data ...", None, 0, 0)
        self.dialog.setWindowTitle("Fetching Data")
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.setCancelButton(None)
        self.dialog.setMinimumDuration(0)
        self.dialog.setFixedSize(500,100)
        self.dialog.show()
        return self.dialog