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

class CustomTagDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Tag")
        self.setFixedSize(300, 140)

        self.station_label = QLabel("Station Name:")
        self.station_input = QLineEdit()

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
        layout.addWidget(self.station_label)
        layout.addWidget(self.station_input)
        layout.addWidget(self.tag_label)
        layout.addWidget(self.tag_input)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        return self.station_input.text().strip(), self.tag_input.text().strip()


class TagManagerWindow(QMainWindow):
    def __init__(self, json_path="tags.json",header=""):
        super().__init__()
        self.json_path = json_path
        self.setWindowTitle("Tag Manager")
        self.resize(500, 400)

        self._load_data()

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([header,"Tag Name"] if type(header) == str and len(header) > 0  else ["Station Name","Tag Name"])                                                                                               
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
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = {}
        else:
            self.data = {}

    def _save_data(self):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def _populate_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for station, tags in self.data.items():
            for tag in tags:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(station))
                self.table.setItem(row, 1, QTableWidgetItem(tag))
        self.table.blockSignals(False)

    def _on_add_row(self):
        dialog = CustomTagDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            station, tag = dialog.get_data()
            if not station or not tag:
                QMessageBox.warning(self, "Invalid", "Both fields are required.")
                return

            # update data model
            self.data.setdefault(station, [])
            if tag in self.data[station]:
                QMessageBox.information(self, "Exists", f"'{tag}' already in '{station}'.")
                return

            self.data[station].append(tag)
            self._save_data()

            # reflect in UI
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(station))
            self.table.setItem(row, 1, QTableWidgetItem(tag))

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

        # remove from bottom up to keep indices valid
        for sel in sorted(selected, key=lambda x: x.row(), reverse=True):
            station = self.table.item(sel.row(), 0).text()
            tag = self.table.item(sel.row(), 1).text()
            if station in self.data and tag in self.data[station]:
                self.data[station].remove(tag)
                if not self.data[station]:
                    del self.data[station]
            self.table.removeRow(sel.row())

        self._save_data()

    def _on_item_changed(self, item):
        row, col = item.row(), item.column()
        old_station = None
        old_tag = None

        # identify original values by reloading JSON
        # (or keep a cache before edit)—for simplicity we reload here
        self._load_data()
        self._populate_table()

        new_station = self.table.item(row, 0).text().strip()
        new_tag = self.table.item(row, 1).text().strip()

        if not new_station or not new_tag:
            QMessageBox.warning(self, "Invalid", "Fields cannot be empty.")
            self._populate_table()
            return

        # overwrite entire data model with the table contents
        new_data = {}
        for r in range(self.table.rowCount()):
            st = self.table.item(r, 0).text().strip()
            tg = self.table.item(r, 1).text().strip()
            new_data.setdefault(st, []).append(tg)

        self.data = new_data
        self._save_data()