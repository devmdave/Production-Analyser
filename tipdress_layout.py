from math import fabs
import sys
from numpy import result_type, true_divide
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QHeaderView
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from Dialog import Dialog
import my_plc
import threading
import datetime 

custom_headers = ['Station', 'Tip Dress Count']
custom_headers2 = ['Station', 'Last Tip Dress']

class TipDressTagWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tip Dress Analysis")
        self.setGeometry(100, 100, 900, 400)

        # --- File name label at the top ---
        self.file_name_label = QLabel(f"File: {'No file selected'}")
        self.file_name_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.file_name_label.setStyleSheet("padding: 8px; color: #1a237e; background: #e3f2fd; border-radius: 6px;")

        # --- Main layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.file_name_label, alignment=Qt.AlignTop)

        # --- Two frames side by side ---
        frames_layout = QHBoxLayout()
        frames_layout.setSpacing(20)

        # --- Left Frame: Tip Dress Count ---
        self.left_frame = QWidget()
        self.left_frame.setFixedWidth(400)
        left_layout = QVBoxLayout(self.left_frame)
        left_label = QLabel("Tip Dress Count")
        left_label.setFont(QFont('Arial', 11, QFont.Bold))
        left_label.setAlignment(Qt.AlignCenter)
        left_label.setStyleSheet("""
            background-color: #0000FF;
            color: white;
            padding: 12px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        """)
        left_layout.addWidget(left_label)
        self.tip_dress_count_table = QTableWidget()
        self.tip_dress_count_table.setFixedHeight(300)
        left_layout.addWidget(self.tip_dress_count_table)

        # --- Right Frame: Last Tip Dress ---
        self.right_frame = QWidget()
        self.right_frame.setFixedWidth(400)
        right_layout = QVBoxLayout(self.right_frame)
        right_label = QLabel("Last Tip Dress")
        right_label.setFont(QFont('Arial', 11, QFont.Bold))
        right_label.setAlignment(Qt.AlignCenter)
        right_label.setStyleSheet("""
            background-color: #0000FF;
            color: white;
            padding: 12px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        """)
        right_layout.addWidget(right_label)
        self.last_tip_dress_table = QTableWidget()
        self.last_tip_dress_table.setFixedHeight(300)
        right_layout.addWidget(self.last_tip_dress_table)

        # Add frames to the horizontal layout
        frames_layout.addWidget(self.left_frame)
        frames_layout.addWidget(self.right_frame)

        # Add frames layout to the main layout
        main_layout.addLayout(frames_layout)

        self.dg = Dialog()
        dg = self.dg.show_progress_dialog()
        
        self.reader_thread = threading.Thread(target=lambda: self.fetch_data(dg))
        self.reader_thread.start()
        
        # self.load_data_to_view()

    def populate_table(self, table, df, custom_headers):
        table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                background-color: #e0e0e0;
                border: 1px solid #000000; 
                gridline-color: 1px solid #000000;               
                selection-background-color: #a0d7ff;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(custom_headers)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)

    def fetch_data(self, dg):
        self.load_tip_dress_count_data()
        self.load_last_tip_dress_data()
        dg.close()
        
    def load_tip_dress_count_data(self):
        result = False
        try:
            print("trying to connect")
            plc = my_plc.Plc('192.168.0.10')
            tags_data = plc.read_tip_dress_count_tags()
            dw = my_plc.data_writer()
            dw.write_to_excel(tags_data, dw.TIP_DRESS_COUNT_DIR)
            result = True
        except Exception as e:
            result = False
        return result

    def load_last_tip_dress_data(self):
        result = False
        try:
            print("trying to connect")
            plc = my_plc.Plc('192.168.0.10')
            tags_data = plc.read_last_tip_dress_tags()
            dw = my_plc.data_writer()
            dw.write_to_excel(tags_data, dw.LAST_TIP_DRESS_DIR)
            result = True
        except Exception as e:
            result = False
        return result
    
    def load_data_to_view(self):
        dw = my_plc.data_writer()
        
        today_str = datetime.datetime.now().strftime('%d-%m-%Y')
        self.tip_dress_count_file = f'./{dw.TIP_DRESS_COUNT_DIR}/{today_str}.xlsx'
        self.last_tip_dress_file = f'./{dw.LAST_TIP_DRESS_DIR}/{today_str}.xlsx'
        try:
            df_tip_dress_count = pd.read_excel(self.tip_dress_count_file)
            df_last_tip_dress = pd.read_excel(self.last_tip_dress_file)

            if len(df_tip_dress_count) > 0 and len(df_last_tip_dress) > 0:
                df_tip_dress_count.columns.values[0] = "Station No"
                df_last_tip_dress.columns.values[0] = "Station No"
                self.populate_table(self.tip_dress_count_table, df_tip_dress_count, custom_headers)
                self.populate_table(self.last_tip_dress_table, df_last_tip_dress, custom_headers2)
                return True
            else:
                self.dg = Dialog()
                self.dg.show_plc_connection_error()
        except FileNotFoundError as e:
            self.dg = Dialog()
            self.dg.show_error_dialog()

def main():
    app = QApplication(sys.argv)
    window = TipDressTagWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()