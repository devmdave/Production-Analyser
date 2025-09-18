import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog

class TagViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Tag Viewer')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.load_button = QPushButton('Load JSON File')
        self.load_button.clicked.connect(self.load_json)

        self.layout.addWidget(self.load_button)

        self.tags_label = QLabel("Tags will be displayed here.")
        self.layout.addWidget(self.tags_label)

        self.setLayout(self.layout)

    def load_json(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter('JSON Files (*.json)')
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            json_file = file_dialog.selectedFiles()[0]
            self.display_tags(json_file)

    def display_tags(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                tags = data.get('tags', [])

                if not tags:
                    self.tags_label.setText('No tags found in the JSON file.')
                    return

                tags_info = ""
                for tag in tags:
                    tags_info += f"Tag: {tag['tag']}, Label: {tag['label']}\n"
                
                self.tags_label.setText(tags_info)

        except Exception as e:
            self.tags_label.setText(f"Error loading file: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = TagViewer()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
