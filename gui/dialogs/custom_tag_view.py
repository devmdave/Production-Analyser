import sys
import os
import json
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QApplication, QMessageBox
)

class CustomTagDialog(QDialog):
    def __init__(self, json_path="tags.json", parent=None):
        super().__init__(parent)
        self.json_path = json_path
        self.setWindowTitle("Enter Tag Details")
        self.setFixedSize(320, 160)

        # Widgets
        self.station_label = QLabel("Station Name:")
        self.station_input = QLineEdit()

        self.tag_label = QLabel("Tag Name:")
        self.tag_input = QLineEdit()

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        # Signals
        self.ok_button.clicked.connect(self.on_accept)
        self.cancel_button.clicked.connect(self.reject)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.station_label)
        layout.addWidget(self.station_input)
        layout.addWidget(self.tag_label)
        layout.addWidget(self.tag_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def on_accept(self):
        station = self.station_input.text().strip()
        tag = self.tag_input.text().strip()

        if not station or not tag:
            QMessageBox.warning(self, "Invalid Input", "Both fields are required.")
            return

        try:
            self.save_to_json(station, tag)
            QMessageBox.information(self, "Success", f"Saved '{tag}' under '{station}'.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data:\n{e}")

    def save_to_json(self, station, tag):
        # Load existing data or start fresh
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        # Ensure structure: { station_name: [tag1, tag2, ...], ... }
        tags = data.get(station, [])
        if tag not in tags:
            tags.append(tag)
            data[station] = tag

        # Write back to JSON
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_data(self):
        return self.station_input.text().strip(), self.tag_input.text().strip()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Optional: pass a different JSON file path
    dialog = CustomTagDialog(json_path="my_station_tags.json")
    if dialog.exec_() == QDialog.Accepted:
        station, tag = dialog.get_data()
        print(f"Station: {station}\nTag: {tag}")

    sys.exit(app.exec_())
