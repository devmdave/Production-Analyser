from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTimeEdit, QDialogButtonBox
from PyQt5.QtCore import QTime

class BackupTimeDialog(QDialog):
    def __init__(self, current_time=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Backup Time")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)

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
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    def show(self):
        self.exec_()

    def get_time(self):
        return self.time_edit.time().toString("HH:mm")

# Example usage:
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dlg = BackupTimeDialog()
    print(dlg.get_time())
    # if dlg.exec_() == QDialog.Accepted:
    #     selected_time = dlg.get_time()
    #     print("New backup time:", selected_time.toString("HH:mm"))
    # else:
    #     print("No time selected.")