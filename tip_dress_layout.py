import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QHeaderView, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from Dialog import Dialog
import my_plc
import datetime

custom_headers = ['ROBOT NAME', 'SET VALUE', 'ACTUAL VALUE']

class Worker(QObject):
    finished = pyqtSignal(bool, str)  #success: bool, message: str

    def __init__(self, tip_dress_file, tip_dress_table):
        super().__init__()
        self.tip_dress_file = tip_dress_file
        self.tip_dress_table = tip_dress_table

    def run(self):
        try:
            #Long-running task: load data from PLC and populate table
            self.load_tip_dress_data()
            success = self.load_data_to_view()
            if success:
                self.finished.emit(True, "Data loaded successfully!")
            else:
                self.finished.emit(False, "Failed to load data: No data available or file not found.")
        except Exception as e:
            self.finished.emit(False, f"An error occurred: {str(e)}")

    def load_tip_dress_data(self):
        result = False
        try:
            print("trying to connect")
            plc = my_plc.Plc('192.168.0.10')
            tags_data = plc.read_tip_dress_tags()
            dw = my_plc.data_writer()
            dw.write_to_excel(tags_data, dw.TIP_DRESS_BACKUP_DIR)
            result = True
        except Exception as e:
            result = False
        return result

    def load_data_to_view(self):
        try:
            #Read Excel file using pandas
            df_tip_dress = pd.read_excel(self.tip_dress_file)

            # Check if dataframe has data
            if len(df_tip_dress) > 0:
                df_tip_dress.columns.values[0] = "ROBOT NAME"
                # Populate the table
                self.populate_table(self.tip_dress_table, df_tip_dress, custom_headers)
                return True
            else:
                return False
        except FileNotFoundError:
            return False

    def populate_table(self, table, df, custom_headers):
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(custom_headers)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)
        table.verticalHeader().setVisible(False)


class CurrentTipDress(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True
        self.setWindowTitle("Production Analyser")
        self.setGeometry(100, 100, 600, 400)  # Adjusted window size

        # --- File name label at the top ---
        self.file_name_label = QLabel("Date: Today's Data")

        self.file_name_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.file_name_label.setStyleSheet("padding: 8px; color: #1a237e; background: #e3f2fd; border-radius: 6px;")

        # --- Mode toggle button ---
        self.mode_toggle_btn = QPushButton("Switch to Light Mode")
        self.mode_toggle_btn.clicked.connect(self._toggle_mode)

        # --- Back button ---
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.close)
        self.back_button.setFixedWidth(100)

        # --- Top layout for label, toggle, and back button ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.file_name_label, alignment=Qt.AlignLeft)
        top_layout.addWidget(self.mode_toggle_btn, alignment=Qt.AlignCenter)
        top_layout.addWidget(self.back_button, alignment=Qt.AlignRight)

        # --- Main layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet(self._get_stylesheet())
        main_layout = QVBoxLayout(central_widget)
        main_layout.addLayout(top_layout)

        # --- Frame for table ---
        self.frame = QWidget()
        layout = QVBoxLayout(self.frame)
        label = QLabel("Tip Dress Data")
        label.setFont(QFont('Arial', 11, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("frame_label")
        layout.addWidget(label)
        self.tip_dress_table = QTableWidget()
        self.tip_dress_table.setFixedHeight(300)
        layout.addWidget(self.tip_dress_table)

        # Add frame to main layout
        main_layout.addWidget(self.frame)

        dw = my_plc.data_writer()
        print("loading today's file")
        today_str = datetime.datetime.now().strftime('%d-%m-%Y')
        self.tip_dress_file = f'./{dw.TIP_DRESS_BACKUP_DIR}/{today_str}.xlsx'

        # Show progress dialog
        self.dg = Dialog()
        self.progress_dialog = self.dg.show_progress_dialog()

        # Create worker and thread
        self.worker = Worker(self.tip_dress_file, self.tip_dress_table)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.on_worker_finished)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def populate_table(self, table, df, custom_headers):
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(custom_headers)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)
        table.verticalHeader().setVisible(False)

    def load_data_to_view(self):
        try:
            # Read Excel file using pandas
            df_tip_dress = pd.read_excel(self.tip_dress_file)

            # Check if dataframe has data
            if len(df_tip_dress) > 0:
                df_tip_dress.columns.values[0] = "ROBOT NAME"
                # Populate the table
                self.populate_table(self.tip_dress_table, df_tip_dress, custom_headers)
                return True
            else:
                return False
        except FileNotFoundError:
            return False

    def _toggle_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.mode_toggle_btn.setText("Switch to Light Mode")
        else:
            self.mode_toggle_btn.setText("Switch to Dark Mode")
        self.setStyleSheet(self._get_stylesheet())

    def on_worker_finished(self, success, message):
        # Close progress dialog
        self.progress_dialog.close()

        # Clean up thread and worker
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

        # Show QMessageBox based on result
        if not success:
            self.dg.show_tip_dress_data_not_found_error()

    def _get_stylesheet(self):
        if self.dark_mode:
            return """
                QWidget {
                    background-color: #34495e;
                    color: #ecf0f1;
                    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QLabel#frame_label {
                    background-color: #002A4D;
                    color: white;
                    padding: 12px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #002A4D;
                    border: none;
                    color: white;
                    padding: 7px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #003A5D;
                }
                QTextEdit {
                    background-color: #1e1e2f;
                    color: #ecf0f1;
                    font-family: Consolas, monospace;
                    font-size: 11pt;
                    padding: 8px;
                }
                QFrame {
                    background-color: #2c3e50;
                    border-radius: 10px;
                    padding: 3px;
                }
                QMenuBar {
                    color: #002A4D;
                    background-color: #C6E5F5;  /* Dark blue-gray */
                    font-weight: bold;
                    color: #002A4D;
                }
                QMenuBar::item {
                    spacing: 3px;
                    padding: 4px 12px;
                    color: #002A4D;
                    background-color: #C6E5F5;  /* Slightly lighter */
                }
                QMenuBar::item:selected {
                    color: #002A4D;
                    background-color: #AAD8F0;  /* Hover color */
                }
                QMenuBar::item:pressed {
                    color: #002A4D;
                    background-color: #AAD8F0;  /* Clicked color */
                }
                QMenu {
                    color: #002A4D;
                    background-color: #C6E5F5;  /* Dropdown background */
                }
                QMenu::item {
                    padding: 5px 20px;
                    color: #002A4D;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: #6ABBE5;
                    color: black;
                }
                QTableWidget {
                    font-size: 10px;
                    background-color: #f5f5f5;
                    color: #002A4D;
                    gridline-color: #cccccc;
                    selection-background-color: #d3d3d3;
                    alternate-background-color: #f0f8ff;
                    font-family: 'Segoe UI';
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QHeaderView::section {
                    background-color: #002A4D;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #aad8f0;
                }
                QHeaderView::section:hover {
                    background-color: #003A5D;
                }
                QScrollBar:vertical {
                    width: 8px;
                    background-color: #f0f0f0;
                }
                QScrollBar::handle:vertical {
                    background-color: #cccccc;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #aaaaaa;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #FFFFFF;
                    color: #002A4D;
                    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                }
                QLabel {
                    color: #002A4D;
                }
                QLabel#frame_label {
                    background-color: #002A4D;
                    color: white;
                    padding: 12px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #002A4D;
                    border: none;
                    color: white;
                    padding: 7px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #003A5D;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #002A4D;
                    font-family: Consolas, monospace;
                    font-size: 11pt;
                    padding: 8px;
                }
                QFrame {
                    background-color: #C6E5F5;
                    border-radius: 10px;
                    padding: 5px;
                }
                QMenuBar {
                    background-color: #C6E5F5;  /* Dark blue-gray */
                    font-weight: bold;
                    color: #002A4D;
                }
                QMenuBar::item {
                    spacing: 3px;
                    padding: 4px 12px;
                    color: #002A4D;
                    background-color: #C6E5F5;  /* Slightly lighter */
                }
                QMenuBar::item:selected {
                    color: #002A4D;
                    background-color: #AAD8F0;  /* Hover color */
                }
                QMenuBar::item:pressed {
                    color: #002A4D;
                    background-color: #AAD8F0;  /* Clicked color */
                }
                QMenu {
                    background-color: #C6E5F5;  /* Dropdown background */
                    color: #002A4D;
                }
                QMenu::item {
                    padding: 5px 20px;
                    color: #002A4D;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: #6ABBE5;
                    color: black;
                }
                QTableWidget {
                    font-size: 10px;
                    background-color: #f5f5f5;
                    color: #002A4D;
                    gridline-color: #cccccc;
                    selection-background-color: #d3d3d3;
                    alternate-background-color: #f0f8ff;
                    font-family: 'Segoe UI';
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QHeaderView::section {
                    background-color: #002A4D;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #aad8f0;
                }
                QHeaderView::section:hover {
                    background-color: #003A5D;
                }
                QScrollBar:vertical {
                    width: 8px;
                    background-color: #f0f0f0;
                }
                QScrollBar::handle:vertical {
                    background-color: #cccccc;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #aaaaaa;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CurrentTipDress()
    window.show()
    sys.exit(app.exec_())
