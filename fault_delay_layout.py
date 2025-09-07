from math import fabs
import sys
from numpy import result_type, true_divide
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel,QHeaderView
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from Dialog import Dialog
import my_plc
import threading
import datetime 

custom_headers = ['Faults', 'Delay']
custom_headers2 = ['Station', 'Fault Delay']



class CurrentFaultDelay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production Analyser")
        self.setGeometry(100, 100, 900, 400)  # Decreased window size

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

        # --- Left Frame: Total Delay ---
        self.left_frame = QWidget()
        self.left_frame.setFixedWidth(400)
        left_layout = QVBoxLayout(self.left_frame)
        left_label = QLabel("Total Delay")
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
        self.fault_delay_table = QTableWidget()
        self.fault_delay_table.setFixedHeight(300)
        left_layout.addWidget(self.fault_delay_table)

        # --- Right Frame: Total Station Fault ---
        self.right_frame = QWidget()
        self.right_frame.setFixedWidth(400)
        right_layout = QVBoxLayout(self.right_frame)
        right_label = QLabel("Total Station Fault")
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
        self.station_fault_table = QTableWidget()
        self.station_fault_table.setFixedHeight(300)
        right_layout.addWidget(self.station_fault_table)

        # Add frames to the horizontal layout
        frames_layout.addWidget(self.left_frame)
        frames_layout.addWidget(self.right_frame)

        # Add frames layout to the main layout
        main_layout.addLayout(frames_layout)

        # Example: populate tables with dummy data
        df = pd.read_excel('./DelayBackup/dummy.xlsx')

        self.dg = Dialog()
        dg = self.dg.show_progress_dialog()
        
        self.reader_thread = threading.Thread(target=lambda: self.fetch_data(dg))
        self.reader_thread.start()
        # self.reader_thread.join()
        
        self.load_data_to_view()
        # self.populate_table(self.fault_delay_table, df, custom_headers)
        # self.populate_table(self.station_fault_table, df,custom_headers2)

    def populate_table(self, table, df,custom_headers):
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
        # table.resizeColumnsToContents()
    
    def fetch_data(self,dg):
        self.load_fault_delay_data()
        self.load_station_fault_data()
        dg.close()
        
    def load_fault_delay_data(self):
        result = False
        try:
            print("trying to connect")
            plc = my_plc.Plc('192.168.0.10')
            tags_data = plc.read_fault_delay_tags()
            dw = my_plc.data_writer()
            dw.write_to_excel(tags_data,dw.FAULT_DELAY_BACKUP_DIR)
            result = True
        except Exception as e:
            result = False

        return result
    def load_station_fault_data(self):
        result = False
        try:
            print("trying to connect")
            plc = my_plc.Plc('192.168.0.10')
            tags_data = plc.read_station_fault_tags()
            dw = my_plc.data_writer()
            dw.write_to_excel(tags_data,dw.STATION_FAULT_DIR)
            result = True
        except Exception as e:
            result = False

        return result
    
    def load_data_to_view(self):
        dw = my_plc.data_writer()
        
        today_str = datetime.datetime.now().strftime('%d-%m-%Y')
        self.fault_delay_file = f'./{dw.FAULT_DELAY_BACKUP_DIR}/{today_str}.xlsx'
        self.station_fault_file = f'./{dw.STATION_FAULT_DIR}/{today_str}.xlsx'
        try:
            # Read Excel file using pandas
            df_fault_delay = pd.read_excel(self.fault_delay_file)
            df_station_fault = pd.read_excel(self.station_fault_file)

            # Split the dataframe into three parts
            if len(df_fault_delay) > 0 and len(df_station_fault) > 0:
                df_fault_delay.columns.values[0] = "Station No"
                df_station_fault.columns.values[0] = "Station No"
                # Populate the three tables
                self.populate_table(self.fault_delay_table, df_fault_delay,custom_headers)
                self.populate_table(self.station_fault_table, df_station_fault,custom_headers2)
                return True
            else:
                self.dg = Dialog()
                self.dg.show_plc_connection_error()
        except FileNotFoundError as e:
            self.dg = Dialog()
            self.dg.show_error_dialog()