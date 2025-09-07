from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListView, QPushButton, QHBoxLayout, QLabel, QDialogButtonBox
from PyQt5.QtCore import QStringListModel, Qt

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
# Example usage:
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dialog = CustomListViewDialog(["Option 1", "Option 2", "Option 3"], title="Custom List Dialog")
    print(dialog.accept_selection())
