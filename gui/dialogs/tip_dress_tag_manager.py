import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QDialog, QLabel,
    QLineEdit, QDialogButtonBox, QComboBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class TipDressTagDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Tip Dress Tag")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedSize(350, 180)

        self.robot_label = QLabel("Robot Name:")
        self.robot_input = QLineEdit()

        self.type_label = QLabel("Tag Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Set Tag", "Actual Tag"])

        self.tag_label = QLabel("Tag Name:")
        self.tag_input = QLineEdit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            orientation=Qt.Horizontal,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.robot_label)
        layout.addWidget(self.robot_input)
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_combo)
        layout.addWidget(self.tag_label)
        layout.addWidget(self.tag_input)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        return self.robot_input.text().strip(), self.type_combo.currentText(), self.tag_input.text().strip()


class TipDressTagManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_names_path = "plc_custom_user_tags/set_names_tags.json"
        self.actual_names_path = "plc_custom_user_tags/actual_names_tags.json"
        self.setWindowTitle("Tip Dress Tag Manager")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(600, 400)

        self._load_data()

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Robot Name", "Tag Type", "Tag Name"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemChanged.connect(self._on_item_changed)

        add_btn = QPushButton("Add Tag")
        del_btn = QPushButton("Delete Selected Tag")
        add_btn.clicked.connect(self._on_add_row)
        del_btn.clicked.connect(self._on_delete_selected)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        self.setCentralWidget(container)

        self._populate_table()

    def _load_data(self):
        os.makedirs("plc_custom_user_tags", exist_ok=True)
        if os.path.exists(self.set_names_path):
            try:
                with open(self.set_names_path, "r", encoding="utf-8") as f:
                    self.set_data = json.load(f)
            except json.JSONDecodeError:
                self.set_data = {}
        else:
            self.set_data = {}

        if os.path.exists(self.actual_names_path):
            try:
                with open(self.actual_names_path, "r", encoding="utf-8") as f:
                    self.actual_data = json.load(f)
            except json.JSONDecodeError:
                self.actual_data = {}
        else:
            self.actual_data = {}

    def _save_data(self):
        with open(self.set_names_path, "w", encoding="utf-8") as f:
            json.dump(self.set_data, f, indent=4, ensure_ascii=False)
        with open(self.actual_names_path, "w", encoding="utf-8") as f:
            json.dump(self.actual_data, f, indent=4, ensure_ascii=False)

    def _populate_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        # Populate set tags
        for robot, tags in self.set_data.items():
            for tag in tags:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(robot))
                self.table.setItem(row, 1, QTableWidgetItem("Set Tag"))
                self.table.setItem(row, 2, QTableWidgetItem(tag))
        # Populate actual tags
        for robot, tags in self.actual_data.items():
            for tag in tags:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(robot))
                self.table.setItem(row, 1, QTableWidgetItem("Actual Tag"))
                self.table.setItem(row, 2, QTableWidgetItem(tag))
        self.table.blockSignals(False)

    def _on_add_row(self):
        dialog = TipDressTagDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            robot, tag_type, tag = dialog.get_data()
            if not robot or not tag:
                QMessageBox.warning(self, "Invalid", "Robot Name and Tag Name are required.")
                return

            if tag_type == "Set Tag":
                data = self.set_data
                path = self.set_names_path
            else:
                data = self.actual_data
                path = self.actual_names_path

            data.setdefault(robot, [])
            if tag in data[robot]:
                QMessageBox.information(self, "Exists", f"'{tag}' already exists for '{robot}' in {tag_type}.")
                return

            data[robot].append(tag)
            self._save_data()

            # Reflect in UI
            self.table.blockSignals(True)
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(robot))
            self.table.setItem(row, 1, QTableWidgetItem(tag_type))
            self.table.setItem(row, 2, QTableWidgetItem(tag))
            self.table.blockSignals(False)

    def _on_delete_selected(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(selected)} selected row(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        # Remove from bottom up to keep indices valid
        for sel in sorted(selected, key=lambda x: x.row(), reverse=True):
            robot = self.table.item(sel.row(), 0).text()
            tag_type = self.table.item(sel.row(), 1).text()
            tag = self.table.item(sel.row(), 2).text()

            if tag_type == "Set Tag":
                data = self.set_data
            else:
                data = self.actual_data

            if robot in data and tag in data[robot]:
                data[robot].remove(tag)
                if not data[robot]:
                    del data[robot]
            self.table.removeRow(sel.row())

        self._save_data()

    def _on_item_changed(self, item):
        row, col = item.row(), item.column()
        robot = self.table.item(row, 0).text().strip()
        tag_type = self.table.item(row, 1).text().strip()
        tag = self.table.item(row, 2).text().strip()

        if not robot or not tag:
            QMessageBox.warning(self, "Invalid", "Robot Name and Tag Name cannot be empty.")
            self._populate_table()
            return

        # Determine which data to update
        if tag_type == "Set Tag":
            data = self.set_data
        elif tag_type == "Actual Tag":
            data = self.actual_data
        else:
            QMessageBox.warning(self, "Invalid", "Tag Type must be 'Set Tag' or 'Actual Tag'.")
            self._populate_table()
            return

        # Rebuild data from table
        new_set_data = {}
        new_actual_data = {}
        for r in range(self.table.rowCount()):
            r_robot = self.table.item(r, 0).text().strip()
            r_type = self.table.item(r, 1).text().strip()
            r_tag = self.table.item(r, 2).text().strip()
            if r_type == "Set Tag":
                new_set_data.setdefault(r_robot, []).append(r_tag)
            elif r_type == "Actual Tag":
                new_actual_data.setdefault(r_robot, []).append(r_tag)

        self.set_data = new_set_data
        self.actual_data = new_actual_data
        self._save_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TipDressTagManagerWindow()
    window.show()
    sys.exit(app.exec_())
