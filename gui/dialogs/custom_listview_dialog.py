from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListView, QLabel, QDialogButtonBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QStringListModel, Qt

class CustomListViewDialog(QDialog):
    def __init__(self, items, title="Select an Item", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.selected_item = None

        layout = QVBoxLayout(self)

        label = QLabel("Please select an item:")
        layout.addWidget(label)

        self.list_view = QListView()
        self.model = QStringListModel(items)
        self.list_view.setModel(self.model)
        layout.addWidget(self.list_view)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_accept(self):
        selected = self.list_view.selectedIndexes()
        if selected:
            self.selected_item = self.model.data(selected[0], Qt.DisplayRole)
            self.accept()
        else:
            self.reject()
