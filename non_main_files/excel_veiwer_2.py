import sys
import time
import pandas as pd
import os
import datetime
from pycomm3 import exceptions
import my_plc
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                           QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit)
from PyQt5.QtGui import  QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QListView, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QStringListModel, QItemSelectionModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class WorkerThread(QThread):
    finished = pyqtSignal()

    def run(self):
        try:
            plc = my_plc.Plc('192.168.0.10')
            tags_data = plc.read_cycletime_tags()
            dw = my_plc.data_writer()
            dw.write_to_excel(tags_data)
        except Exception as e:
            pass
        time.sleep(3)  # Simulate a long task
        self.finished.emit()


class ExcelViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production Analyser")
        self.setGeometry(100, 100, 1200, 600)
        self.cycle_time = 0
        self.file_path = 'production.xlsx'
       
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        # main_layout = QVBoxLayout(self.central_widget)
        
        # # Create horizontal layout for tables
        # tables_layout = QHBoxLayout() #change to QHBoxLayout for horizontal layout or Change to QVBoxLayout for vertical layout
        
        # # Create three table frames
        # self.left_frame = self.create_table_frame("Production Data")
        # self.middle_frame = self.create_table_frame("Delay in Production")
        # self.right_frame = self.create_table_frame("Total Delay in Production (Stationwise)")
        


        # # Add frames to horizontal layout
        # tables_layout.addWidget(self.left_frame)
        # tables_layout.addWidget(self.middle_frame)
        # tables_layout.addWidget(self.right_frame)
        

        # # Create control panel layout
        # control_panel = QHBoxLayout()
        
        # # Create cycle time input
        # cycle_label = QLabel("Cycle Time:")
        # cycle_label.setFont(QFont('Arial', 10, QFont.Bold))
        # self.cycle_input = QLineEdit()
        # self.cycle_input.setFixedWidth(50)
        # self.cycle_input.setText("92")  # Default value
        # self.cycle_input.returnPressed.connect(self.on_update_clicked)
        
        # # Create update button
        # update_button = QPushButton("SET CYCLETIME")
        # update_button.clicked.connect(self.on_update_clicked)
        # show_current_cycletime = QPushButton("SHOW CURRENT DATA")
        # # update_button.clicked.connect(self.on_update_clicked)
        
        # # Add widgets to control panel
        # control_panel.addWidget(cycle_label)
        # control_panel.addWidget(self.cycle_input)
        # control_panel.addWidget(update_button)
        # control_panel.addWidget(show_current_cycletime)
        # control_panel.addStretch()  # Pushes widgets to the left

        # main_layout.addLayout(control_panel)
        # # Add tables layout to main layout
        # main_layout.addLayout(tables_layout)
        
        # # Create tables
        # self.table1 = QTableWidget()
        # self.table2 = QTableWidget()
        # self.table3 = QTableWidget()
        
        # # Add tables to their respective frames
        # self.left_frame.layout().addWidget(self.table1)
        # self.middle_frame.layout().addWidget(self.table2)
        # self.right_frame.layout().addWidget(self.table3)
        self.show_data_veiw()
    
    def start_task(self):
        self.dialog = QProgressDialog("PLease Wait while we are loading PLC Data ...", None, 0, 0, self)
        self.dialog.setWindowTitle("Fetching Data")
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.setCancelButton(None)
        self.dialog.setMinimumDuration(0)
        self.dialog.setFixedSize(500,100)
        self.dialog.show()

        self.thread = WorkerThread()
        self.thread.finished.connect(self.load_plc_data_now)
        self.thread.start()

    def load_plc_data_now(self):
        today_str = datetime.datetime.now().strftime('%d-%m-%Y')
        self.file_path = f'./CycleTimeBackup/{today_str}.xlsx'
        is_data_loaded = self.load_data_to_veiw()
        self.dialog.close()
        if not is_data_loaded:
            self.show_error_dialog()
        elif is_data_loaded:
            self.show_success_dialog()            

    def show_success_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Connection Info")
        msg.setText("PLC Connection Successfull! \n We have fetched the data successfully.")
        msg.setStandardButtons(QMessageBox.Ok)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: lightgreen;
                font-size: 14px;
            }
            QLabel {
                color: green;
                font-weight: bold;
            }
            QPushButton {
                background-color: green;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: green;
            }
        """)

        msg.exec_()

    def show_no_files_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Automated Production Analyser")
        msg.setText("No previous records found. \n We do not have any backup data at this moment.")
        msg.setStandardButtons(QMessageBox.Ok)
        # msg.setStyleSheet("""
        #     QMessageBox {
        #         font-size: 14px;
        #     }
        #     QLabel {
        #         font-weight: bold;
        #     }
        #     QPushButton {
        #         padding: 5px 15px;
        #         border-radius: 5px;
        #     }
        # """)

        msg.exec_()

    def show_error_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Connection Error")
        msg.setText("PLC connection failed! \n Please check your PLC connection.")
        msg.setStandardButtons(QMessageBox.Ok)

        # 🔴 Red-themed styling
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffdddd;
                font-size: 14px;
            }
            QLabel {
                color: #b00000;
                font-weight: bold;
            }
            QPushButton {
                background-color: #b00000;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d00000;
            }
        """)

        msg.exec_()

    def on_update_clicked(self):
        try:
            self.cycle_time = int(self.cycle_input.text())
            # Update tables with new cycle time
            self.load_data_to_veiw()
            
        except ValueError:
            print("Please enter a valid number for cycle time")

    def create_table_frame(self, title):
        frame = QWidget()
        layout = QVBoxLayout(frame)
        
        # Add title label
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont('Arial', 10, QFont.Bold))
        label.setStyleSheet("background-color: #0000FF; padding: 25px; color: white;")
        layout.addWidget(label)
        
        return frame 
    
    def load_data_to_veiw(self):
        try:
            # Read Excel file using pandas
            df = pd.read_excel(self.file_path)
             
            # Split the dataframe into three parts
            df.columns.values[0] = 'Station No'
            
            # Populate the three tables
            self.populate_table(self.table1, df)

            delaydf = df.copy()
            self.get_delay_df(delaydf, self.cycle_time)
            self.populate_delay_table(self.table2, delaydf)
            self.populate_delay_total(self.table3, delaydf)
            return True
        except FileNotFoundError as e:
            return False
    
    def populate_delay_table(self, table, df):

        # Calculate row sums for numeric columns
        row_sums = df.select_dtypes(include=['int64', 'float64']).sum(axis=1)
        
        # Set table dimensions (add 1 row for totals and 1 column for row sums)
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1] + 1)
        
        # Set headers
        headers = [str(col) for col in df.columns] + ['Row Total']
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)

        # Populate table with data
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):       
                item = QTableWidgetItem(str(df.iloc[row, col]))
                table.setItem(row, col, item)


            # Add row sum in the last column
            row_sum_item = QTableWidgetItem(f"{row_sums[row]}")
            row_sum_item.setBackground(QColor(200, 230, 255))  # Light purple background(230, 230, 250)
            row_sum_item.setFont(QFont('Arial', 8, QFont.Bold))
            table.setItem(row, df.shape[1], row_sum_item)
            table.setRowHeight(row,10)
        
        table.setStyleSheet("""
            QTableWidget { 
                font-size: 10px;
                background-color: #f5f5f5;
                gridline-color: #0000FF;
                selection-background-color: #a0d7ff;
                font-family: 'Segoe UI';
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #c0c0c0;
            }
        """)
        # Adjust column widths
        table.resizeColumnsToContents()

    def populate_table(self, table, df):
        # Set table dimensions (add 1 row for totals and 1 column for row sums)
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])

        # Set headers
        headers = [str(col) for col in df.columns]
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False) 
        # df.iloc[0,0] = "Station Name"
        # Populate table with data and row sums
        for row in range(df.shape[0]):
            # Populate regular data
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                if type(df.iloc[row, col]) != str:
                    if int(df.iloc[row, col]) >= self.cycle_time:
                        item.setBackground(QColor(220, 60, 34))
                table.setItem(row, col, item)
            
        table.setStyleSheet("""
            QTableWidget {
                
                font-size: 10px;
                background-color: #f5f5f5;
                gridline-color: #0000FF;
                selection-background-color: #a0d7ff;
                font-family: 'Segoe UI';
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #c0c0c0;
            }
        """)

        # Adjust column widths 
        table.resizeColumnsToContents()

    def populate_delay_total(self, table, df):
               
        # Calculate row sums for numeric columns
        df.insert(1,"Total", df.select_dtypes(include=['int64', 'float64']).sum(axis=1),True)
        
        table.setRowCount(df.shape[0])
        table.setColumnCount(2)
        # Set headers
        headers = [str(col) for col in df.columns]
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        
        # Populate table with data
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):       
                item = QTableWidgetItem(str(df.iloc[row, col]))                 
                item.setTextAlignment(Qt.AlignCenter) 
                table.setItem(row, col, item)
        
        table.setStyleSheet("""
            QTableWidget {
                font-size: 10px;
                background-color: #e0e0e0;
                border: 2px solid #000000; 
                gridline-color: 2px solid #000000;               
                selection-background-color: #a0d7ff;
                font-family: 'Segoe UI';
                
            }

            QHeaderView::section {
                background-color: #e0e0e0;
                font-weight: bold;
                padding: 4px;
                
            }
                 """)

    def show_file_list(self):
        files = os.listdir("CycleTimeBackup") if os.path.exists("CycleTimeBackup") else self.show_no_files_dialog()
        
        if not files:
            return
        self.central_widget.destroy()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        header_label = QLabel("Production Data")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding-bottom: 8px;")

        # List of files
        self.model = QStringListModel(files)

        # List view
        list_view = QListView()
        list_view.setModel(self.model)

        list_view.clicked.connect(lambda index: self.list_view_item_clicked(index=index))

        # Create control panel layout
        control_panel = QHBoxLayout()
        
        # Create cycle time input
        cycle_label = QLabel("Cycle Time:")
        cycle_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.cycle_input = QLineEdit()
        self.cycle_input.setFixedWidth(50)
        self.cycle_input.setText(str(self.cycle_time))  # Default value
        self.cycle_time = int(self.cycle_input.text())

        self.cycle_input.returnPressed.connect(self.on_update_clicked)
        
        # Create update button
        update_button = QPushButton("TODAY'S DATA")
        update_button.clicked.connect(self.start_task)
        show_current_cycletime = QPushButton("BACKUP DATA")
        # update_button.clicked.connect(self.on_update_clicked)
        
        # Add widgets to control panel
        control_panel.addWidget(cycle_label)
        control_panel.addWidget(self.cycle_input)
        control_panel.addWidget(update_button)
        control_panel.addWidget(show_current_cycletime)
        control_panel.addStretch()  # Pushes widgets to the left

        # Layout
        layout = QVBoxLayout(self.central_widget)
        layout.addLayout(control_panel)
        layout.addWidget(header_label)
        layout.addWidget(list_view)
        
    def show_data_veiw(self):
        self.central_widget.destroy()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        
        # Create horizontal layout for tables
        tables_layout = QHBoxLayout() #change to QHBoxLayout for horizontal layout or Change to QVBoxLayout for vertical layout
        
        # Create three table frames
        self.left_frame = self.create_table_frame("Production Data")
        self.middle_frame = self.create_table_frame("Delay in Production")
        self.right_frame = self.create_table_frame("Total Delay in Production (Stationwise)")
        


        # Add frames to horizontal layout
        tables_layout.addWidget(self.left_frame)
        tables_layout.addWidget(self.middle_frame)
        tables_layout.addWidget(self.right_frame)
        

        # Create control panel layout
        control_panel = QHBoxLayout()
        
        # Create cycle time input
        cycle_label = QLabel("Cycle Time:")
        cycle_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.cycle_input = QLineEdit()
        self.cycle_input.setFixedWidth(50)
        self.cycle_input.setText(str(self.cycle_time))  # Default value
        self.cycle_time = int(self.cycle_input.text())
        self.cycle_input.returnPressed.connect(self.on_update_clicked)
        
        # Create update button
        tdy_data_btn = QPushButton("TODAY's DATA")
        tdy_data_btn.clicked.connect(self.start_task)
        backup_data_btn = QPushButton("BACKUP DATA")
        backup_data_btn.clicked.connect(self.show_file_list)
        
        # Add widgets to control panel
        control_panel.addWidget(cycle_label)
        control_panel.addWidget(self.cycle_input)
        control_panel.addWidget(tdy_data_btn)
        control_panel.addWidget(backup_data_btn)
        control_panel.addStretch()  # Pushes widgets to the left

        main_layout.addLayout(control_panel)
        # Add tables layout to main layout
        main_layout.addLayout(tables_layout)
        
        # Create tables
        self.table1 = QTableWidget()
        self.table2 = QTableWidget()
        self.table3 = QTableWidget()
        
        # Add tables to their respective frames
        self.left_frame.layout().addWidget(self.table1)
        self.middle_frame.layout().addWidget(self.table2)
        self.right_frame.layout().addWidget(self.table3)
        
    def list_view_item_clicked(self,index):
        self.show_data_veiw()
        self.file_path = './CycleTimeBackup/'+self.model.data(index,0)
        self.on_update_clicked()

    def get_delay_df(self,df, cycle_time):
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns    
        df[numeric_columns] = (df[numeric_columns] - (cycle_time)).clip(lower=0)

def main():
    app = QApplication(sys.argv)
    viewer = ExcelViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()