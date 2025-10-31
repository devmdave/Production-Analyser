import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QDialog, QLabel,
    QLineEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt

class ParameterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Parameter")
        self.setFixedSize(300, 140)

        self.param_label = QLabel("Parameter Name:")
        self.param_input = QLineEdit()

        self.value_label = QLabel("Value:")
        self.value_input = QLineEdit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            orientation=Qt.Horizontal,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.param_label)
        layout.addWidget(self.param_input)
        layout.addWidget(self.value_label)
        layout.addWidget(self.value_input)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        return self.param_input.text().strip(), self.value_input.text().strip()


class ParameterManagerWindow(QMainWindow):
    def __init__(self, json_path="config.json"):
        super().__init__()
        self.json_path = json_path
        self.setWindowTitle("Parameter Manager")
        self.resize(500, 400)

        self._load_data()

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemChanged.connect(self._on_item_changed)

        add_btn = QPushButton("Add Parameter")
        del_btn = QPushButton("Delete Selected Parameter")
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
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    # Expecting {"parameters": [{"name": ..., "value": ...}, ...]}
                    params_list = content.get("parameters", [])
                    self.data = {p.get("name", ""): p.get("value", "") for p in params_list}
            except json.JSONDecodeError:
                self.data = {}
        else:
            self.data = {}

    def _save_data(self):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.json_path) or '.', exist_ok=True)
        # Convert self.data dict to list of {"name":..., "value":...} dicts
        params_list = [{"name": k, "value": v} for k, v in self.data.items()]
        content = {"parameters": params_list}
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4, ensure_ascii=False)

    def _populate_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for param, value in self.data.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(param))
            self.table.setItem(row, 1, QTableWidgetItem(str(value)))
        self.table.blockSignals(False)

    def _on_add_row(self):
        if self.table.rowCount() >= 8:
            QMessageBox.warning(self, "Limit Reached", "Maximum 8 parameters allowed.")
            return

        dialog = ParameterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            param, value = dialog.get_data()
            if not param:
                QMessageBox.warning(self, "Invalid", "Parameter name is required.")
                return

            if param in self.data:
                QMessageBox.information(self, "Exists", f"Parameter '{param}' already exists.")
                return

            self.data[param] = value
            self._save_data()

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(param))
            self.table.setItem(row, 1, QTableWidgetItem(value))

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

        for sel in sorted(selected, key=lambda x: x.row(), reverse=True):
            param = self.table.item(sel.row(), 0).text()
            if param in self.data:
                del self.data[param]
            self.table.removeRow(sel.row())

        self._save_data()

    def _on_item_changed(self, item):
        row, col = item.row(), item.column()
        param_item = self.table.item(row, 0)
        value_item = self.table.item(row, 1)

        if not param_item or not value_item:
            return

        param = param_item.text().strip()
        value = value_item.text().strip()

        if not param:
            QMessageBox.warning(self, "Invalid", "Parameter name cannot be empty.")
            self._populate_table()
            return

        # Check for duplicate parameter names in table
        param_counts = {}
        for r in range(self.table.rowCount()):
            p = self.table.item(r, 0).text().strip()
            param_counts[p] = param_counts.get(p, 0) + 1
        if param_counts.get(param, 0) > 1:
            QMessageBox.warning(self, "Duplicate", f"Parameter '{param}' already exists.")
            self._populate_table()
            return

        # Update data model from table contents
        new_data = {}
        for r in range(self.table.rowCount()):
            p = self.table.item(r, 0).text().strip()
            v = self.table.item(r, 1).text().strip()
            new_data[p] = v

        self.data = new_data
        self._save_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParameterManagerWindow("plc_custom_user_tags\\dashboard_tags.json")
    window.show()
    sys.exit(app.exec_())
