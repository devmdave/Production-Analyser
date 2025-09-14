import os
from TagManager import TagManagerWindow
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtWidgets import QListView, QWidget, QVBoxLayout, QLabel,QProgressDialog
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import (
    QMainWindow,
    QTimeEdit,
)
from PyQt5.QtCore import Qt
from Dialog import *
import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QSpacerItem,QAction
)
import my_plc,time, datetime
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from summary_card import SummaryCard

class WorkerThread(QThread):
    finished = pyqtSignal()
    def run(self):
        try:
            print("trying to connect")
            plc = my_plc.Plc('192.168.0.10')
            tags_data = plc.read_cycletime_tags()
            dw = my_plc.data_writer()
            dw.write_to_excel(tags_data,dw.CYCLETIME_BACKUP_DIR)
        except Exception as e:
            print("Exception occured in Worker Thread:\n" + str(e))

        time.sleep(3)  # Simulate a long task
        self.finished.emit()

class CustomTimeEdit(QTimeEdit):
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            # Ignore Backspace and Delete
            print("Blocked key:", event.key())
            return
        super().keyPressEvent(event)

qss = """
        QMenuBar {
            background-color: #C6E5F5;  /* Dark blue-gray */
            font-weight: bold;
            color: #002A4D;
        }

        QMenuBar::item {
            spacing: 3px;
            padding: 4px 12px;
            background-color: #C6E5F5;  /* Slightly lighter */
        }

        QMenuBar::item:selected {
            background-color: #AAD8F0;  /* Hover color */
        }

        QMenuBar::item:pressed {
            background-color: #AAD8F0;  /* Clicked color */
        }

        QMenu {
            background-color: #C6E5F5;  /* Dropdown background */
            
        }

        QMenu::item {
            padding: 5px 20px;
            background-color: transparent;
        }

        QMenu::item:selected {
            background-color: #6ABBE5;
            color: black;
        }
        """
class MyWindow(QMainWindow):
    EMPTY_DATAFRAME = "EMPTY"
    LOAD_DATA_FAILED = "LOAD_FAILED"
    LOAD_DATA_SUCCESS = "LOAD_SUCCESS"

    def __init__(self):
        super().__init__()
        self.active_dashboard = True
        self.setWindowTitle("Production Analyser")
        self.setFixedSize(1200,600)
        self.setGeometry(100, 100, 1200, 600)
        self.setWindowIcon(QIcon("icon.png"))  # Repla
        self.cycle_time = 0
        self.file_path = "production.xlsx"
        self.Dialog = Dialog()
        self.dlg = BackupTimeDialog()
        edit_cyctime_win = TagManagerWindow(json_path="plc_custom_user_tags\\cycle_time_tags.json")
        edit_fault_delay_win = TagManagerWindow(json_path="plc_custom_user_tags\\station_fault_tags.json")
        edit_station_fault_win = TagManagerWindow(json_path="plc_custom_user_tags\\fault_delay_tags.json")
        edit_tip_dress_win = TagManagerWindow(json_path="plc_custom_user_tags\\tip_dress_tags.json")
        edit_tip_change_win = TagManagerWindow(json_path="plc_custom_user_tags\\tip_dress_tags.json")
        edit_dashboard_win = TagManagerWindow(json_path="plc_custom_user_tags\\dashboard_tags.json")
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Menu bar

        self.menu_bar = self.menuBar() 
        self.menu_bar.setStyleSheet(qss)

        # Menu bar
        cycle_menu = self.menu_bar.addMenu("Cycle Time")
        fault_menu = self.menu_bar.addMenu("Fault Delay")
        tip_dress_menu = self.menu_bar.addMenu("Tip Dress")
        edit_tag_menu = self.menu_bar.addMenu("Edit Tag")
        setting_menu = self.menu_bar.addMenu("Setting")
        

        #menu bar actions
        self.view_cycle_action = QAction("Veiw Backup Data", self)
        cycle_menu.addAction(self.view_cycle_action)

        self.view_current_cycle_action = QAction("Veiw Current Data", self)
        cycle_menu.addAction(self.view_current_cycle_action)

        self.view_current_fault_action = QAction("View Fault Delay (Current)", self)
        fault_menu.addAction(self.view_current_fault_action)

        self.view_backup_fault_action = QAction("View Fault Delay (Backup)", self)
        fault_menu.addAction(self.view_backup_fault_action)
        
        self.tip_dressing_action = QAction("Tip Dress Data",self) # show tip dressing data 
        tip_dress_menu.addAction(self.tip_dressing_action)
        
        self.tip_change_action = QAction("Tip Change Data",self)
        tip_dress_menu.addAction(self.tip_change_action)

        self.edit_cycletime_tag_action = QAction("Cycle time Tag",self) 
        edit_tag_menu.addAction(self.edit_cycletime_tag_action)

        self.edit_stationfault_tag_action = QAction("Station Fault Tag",self) 
        edit_tag_menu.addAction(self.edit_stationfault_tag_action)

        self.edit_faultdelay_tag_action = QAction("Fault Delay Tag",self) 
        edit_tag_menu.addAction(self.edit_faultdelay_tag_action)

        self.edit_tipdress_tag_action = QAction("Tip Dress Tag",self) 
        edit_tag_menu.addAction(self.edit_tipdress_tag_action)

        self.edit_tipchange_tag_action = QAction("Tip Change Tag",self) 
        edit_tag_menu.addAction(self.edit_tipchange_tag_action)

        self.edit_dashboard_tag_action = QAction("Dashboard Tag",self) 
        edit_tag_menu.addAction(self.edit_dashboard_tag_action)

        self.view_current_cycle_action.triggered.connect(lambda: (self.cycletime_current_layout(), self.start_task()))
        # self.view_current_cycle_action.triggered.connect(lambda: self.cycletime_current_layout())

        self.set_backup_time = QAction("Set New Backup Time", self)
        self.set_backup_time.triggered.connect(lambda: self.dlg.show()) #Placeholder action
        
        setting_menu.addAction(self.set_backup_time)

        self.get_backup_time = QAction("Show Saved Backup Time", self)
        self.get_backup_time.triggered.connect(lambda: self.label.setText("Get Backup Time") ) # Placeholder action
                
        setting_menu.addAction(self.get_backup_time)

        self.edit_cycletime_tag_action.triggered.connect(lambda: edit_cyctime_win.show())
        self.edit_faultdelay_tag_action.triggered.connect(lambda: edit_fault_delay_win.show())
        self.edit_stationfault_tag_action.triggered.connect(lambda: edit_station_fault_win.show())
        self.edit_tipchange_tag_action.triggered.connect(lambda: edit_tip_change_win.show())
        self.edit_tipdress_tag_action.triggered.connect(lambda:edit_tip_dress_win.show())
        self.edit_dashboard_tag_action.triggered.connect(lambda:edit_dashboard_win.show())

    def main_window(self):
        try:
            
            self.central_widget.destroy()
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
        except Exception as e:
            pass
        self.active_dashboard = True
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setSpacing(50)
        main_layout.setAlignment(Qt.AlignTop)
        
        # Create layout
        header_layout = QHBoxLayout()
        status_layout = QHBoxLayout()
            
        # Logo setup
        logo_label = QLabel()
        pixmap = QPixmap("logo.png")  # Replace with your logo path
        logo_label.setPixmap(pixmap)
        logo_label.setFixedSize(25, 25)  # Optional: resize logo
        logo_label.setScaledContents(True)

        # Text label setup
        text_label = QLabel("Dashboard")
        text_label.setStyleSheet("color:#002A4D; font-size: 18px; font-weight: bold;")

        header_layout.setSpacing(10)
        # Add widgets to layout
        header_layout.addWidget(logo_label)
        header_layout.addWidget(text_label)

        verticalSpacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        #verticalSpacer1 = QSpacerItem(50, 50, QSizePolicy.Minimum, QSizePolicy.Minimum)
        horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Maximum)
        main_layout.addItem(verticalSpacer)
        main_layout.addLayout(header_layout)
        

        # Live Status Bar
        self.status_label = QLabel("PLC Connection Status: Running")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.status_label.setStyleSheet("color: #ffffff; background: #388e3c; border-radius:15px; " 
                                        "padding: 8px; ")
        self.status_label.setFixedWidth(300)
        self.status_label.setAlignment(Qt.AlignCenter)

        # DateTime Display (auto-updating)
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Segoe UI", 10))
        self.datetime_label.setStyleSheet("color: #37474f;")
        self.datetime_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.datetime_label)
        self.update_datetime()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

        # Summary Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignCenter)

        self.card_prod = SummaryCard("Today's Production (units)", "...", "#002A4D")
        self.card_prod.show(cards_layout)
        self.card_delay = SummaryCard("Total Delay (min)", "...", "#002A4D")
        self.card_delay.show(cards_layout)
        self.card_shiftA = SummaryCard("Shift A Production (units)", "...", "#002A4D")        
        self.card_shiftA.show(cards_layout)
        self.card_shiftB = SummaryCard("Shift B Production (units)", "...", "#002A4D")
        self.card_shiftB.show(cards_layout)

        main_layout.addLayout(cards_layout)

        # Navigation Buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(30)
        nav_layout.setAlignment(Qt.AlignCenter)

        btn1 = QPushButton("Backup Cycle Time")
        btn2 = QPushButton("Current Cycle Time")
        btn3 = QPushButton("Station Faults")
        btn4 = QPushButton("Export Report")

        for btn, color in zip(
            [btn1, btn2, btn3, btn4],
            ["#002A4D", "#002A4D", "#002A4D", "#002A4D"]
        ):
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(170)
            btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 10px;
                    padding: 12px;
                }}
                QPushButton:hover {{
                    background-color: #C6E5F5;
                    color: #002A4D;
                    border: 1px solid #002A4D;

                }}
            """)
            nav_layout.addWidget(btn)

        main_layout.addLayout(nav_layout)
        main_layout.addLayout(status_layout)
        #main_layout.addItem(verticalSpacer1)
        
                
        status_layout.addItem(horizontalSpacer)
        status_layout.addWidget(self.status_label)


        # Footer
        footer = QLabel("© 2025 Madhav Dave. All rights reserved.")
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet("color: #90a4ae; margin-top: 30px;")
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)

    def get_last_bcktime(self):
        return f"Last Backup Synced: {os.getenv("LAST_BACKUP_TIME")}" if os.getenv("LAST_BACKUP_TIME") else "No backup time found."



    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.datetime_label.setText(now.toString("dddd, dd MMMM yyyy - hh:mm:ss AP") + f"\n\n {self.get_last_bcktime()}")

    def cycletime_backup_layout(self):
        self.timer.stop()
        self.setGeometry(100, 100, 500, 600)

        files = (
            os.listdir("CycleTimeBackup")
            if os.path.exists("CycleTimeBackup")
            else self.Dialog.show_error_dialog()
        )

        if not files:
            return
        #self.central_widget.destroy()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        header_label = QLabel("Please Choose a backup record from below list of the available records to view it.")
        header_label.setStyleSheet(
            "font-size: 14px; font-weight: normal; padding-bottom: 8px;"
        )
        for file in files:
            files.remove(file)
            file = file.replace(".xlsx", "")
            files.append(file)
            
        self.model = QStringListModel(files)
        # List view
        list_view = QListView()
        list_view.setFixedWidth(500)

        list_view.setModel(self.model)
        list_view.clicked.connect(
            lambda index: self.list_view_item_clicked(index=index)
        )
        # Create control panel layout
        control_panel = QHBoxLayout()


        # file name display
        self.file_name_label = QLabel(f"File: {"No file selected"}")
        self.file_name_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.file_name_label.setStyleSheet("padding: 5px;")


        control_panel.addWidget(self.file_name_label, alignment=Qt.AlignLeft)


        # Layout
        layout = QVBoxLayout(self.central_widget)
        layout.addLayout(control_panel)
        layout.addWidget(header_label)
        layout.addWidget(list_view)

    def list_view_item_clicked(self, index):
        self.cycletime_current_layout()
        self.file_path = "./CycleTimeBackup/" + self.model.data(index, 0)+ ".xlsx"
        self.file_name_label.setText(f"Record Dated: {self.model.data(index,0)}")
        self.load_data_to_veiw()

    def cycletime_current_layout(self):
        self.timer.stop()
        self.central_widget.destroy()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)

        # Create horizontal layout for tables
        tables_layout = (QHBoxLayout())  # change to QHBoxLayout for horizontal layout or Change to QVBoxLayout for vertical layout

        # Create three table frames
        self.left_frame = self.create_table_frame("Production Data")
        self.middle_frame = self.create_table_frame("Delay in Production")
        self.right_frame = self.create_table_frame("Process Delay \n (Stationwise)")

        # Add frames to horizontal layout
        tables_layout.addWidget(self.left_frame,stretch=4)
        tables_layout.addWidget(self.middle_frame,stretch=4)
        self.right_frame.setFixedWidth(200)
        tables_layout.addWidget(self.right_frame,stretch=1)


        # Create control panel layout
        control_panel = QHBoxLayout()
        control_panel.setContentsMargins(0, 0, 50, 0)

        
        # Create back button to go to dashboard
        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda : self.main_window())

                                    

        # Create cycle time input
        cycle_label = QLabel("Cycle Time:")
        cycle_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.cycle_input = QLineEdit()
        self.cycle_input.setFixedWidth(100)
        self.cycle_input.setText(str(self.cycle_time))  # Default value
        self.cycle_input.setPlaceholderText("Enter cycle time")
        self.cycle_input.returnPressed.connect(self.load_data_to_veiw)

        
        # File name display
        self.file_name_label = QLabel(f"File: {"No file selected"}")
        self.file_name_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.file_name_label.setStyleSheet("padding: 5px;")

        # # Time picker setup
        # self.time_edit = CustomTimeEdit()
        # self.time_edit.setDisplayFormat("hh:mm")  # You can customize this format
        # self.time_edit.setTime(QTime.currentTime())  # Set current time as default
        # # Button setup
        # self.button = QPushButton("SET BACKUP TIME")
        # self.button.clicked.connect(self.set_backuptime)

        # # Add widgets to control panel
        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)

        control_panel.addWidget(back_button, alignment=Qt.AlignLeft)
        control_panel.addWidget(cycle_label, alignment=Qt.AlignLeft)
        control_panel.addWidget(self.cycle_input, alignment=Qt.AlignLeft)
        control_panel.addItem(spacer)
        control_panel.addWidget(self.file_name_label, alignment=Qt.AlignLeft)

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

        self.setGeometry(100, 100, 1200, 600)

    def load_data_to_veiw(self):
        try:
            self.cycle_time = int(self.cycle_input.text())
            # Read Excel file using pandas
            df = pd.read_excel(self.file_path)
            # Split the dataframe into three parts
            if not df.empty:
                df.columns.values[0] = "Station No"
                # Populate the three tables
                self.populate_table(self.table1, df)

                delaydf = df.copy()
                self.get_delay_df(delaydf, self.cycle_time)
                self.populate_delay_table(self.table2, delaydf)
                self.populate_delay_total(self.table3, delaydf)
                return MyWindow.LOAD_DATA_SUCCESS
            else:
                return MyWindow.EMPTY_DATAFRAME
        except FileNotFoundError:
            return MyWindow.LOAD_DATA_FAILED

    def populate_delay_table(self, table, df):
        # Calculate row sums for numeric columns
        row_sums = df.select_dtypes(include=["int64", "float64"]).sum(axis=1)
        
        # Set table dimensions (add 1 row for totals and 1 column for row sums)
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1] + 1)

        # Set headers
        headers = [str(col) for col in df.columns] + ["Row Total"]
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)

        # Populate table with data
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                if type(df.iloc[row, col]) != str:
                    if int(df.iloc[row, col]) > 0 :
                        item.setBackground(QColor(255, 255, 100))
                table.setItem(row, col, item)

            # Add row sum in the last column
            row_sum_item = QTableWidgetItem(f"{row_sums[row]}")
            row_sum_item.setBackground(
                QColor(200, 230, 255)
            )  # Light purple background(230, 230, 250)
            row_sum_item.setFont(QFont("Arial", 8, QFont.Bold))
            table.setItem(row, df.shape[1], row_sum_item)
            table.setRowHeight(row, 10)

        table.setStyleSheet(
            """
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
        """
        )
        self.highlight_max_values(table)
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
                        item.setBackground(QColor(255, 255, 100))
                table.setItem(row, col, item)
            table.setRowHeight(row, 10)
        table.setStyleSheet(
            """
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
        """
        )

        # Adjust column widths
        table.resizeColumnsToContents()

    def populate_delay_total(self, table, df):


        # Calculate row sums for numeric columns
        df.insert(
            1, "Total", df.select_dtypes(include=["int64", "float64"]).sum(axis=1), True
        )

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

        table.setStyleSheet(
            """
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
                 """
        )
        self.highlight_max_values(table)

    def create_table_frame(self, title):
        frame = QWidget()
        layout = QVBoxLayout(frame)

        # Add title label
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 10, QFont.Bold))
        label.setStyleSheet("background-color: #002A4D; padding: 25px; color: white;")
        layout.addWidget(label)

        return frame

    def get_delay_df(self, df, cycle_time):
        numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns
        df[numeric_columns] = (df[numeric_columns] - (cycle_time)).clip(lower=0)

    def start_task(self):
        dg = self.Dialog.show_progress_dialog()
        self.thread = WorkerThread()
        self.thread.finished.connect(lambda: self.load_plc_data_now(dg))
        self.thread.start()
    
    def load_plc_data_now(self,dg): 
        today_str = datetime.datetime.now().strftime('%d-%m-%Y')
        self.file_path = f'./CycleTimeBackup/{today_str}.xlsx'
        response = self.load_data_to_veiw()
        dg.close()

        self.Dialog = Dialog()
        if response == MyWindow.EMPTY_DATAFRAME:
            self.Dialog.show_no_tags_error()
        elif response == MyWindow.LOAD_DATA_FAILED:
            self.Dialog.show_file_not_found_error()
        elif response == MyWindow.LOAD_DATA_SUCCESS:
            self.Dialog.show_success_data_loaded()


    def highlight_max_values(self,table):
        rows = table.rowCount()
        cols = table.columnCount()

        for col in range(cols):
            max_val = float('-inf')
            max_row = -1

            # Find max value in the column
            for row in range(rows):
                item = table.item(row, col)
                if item:
                    try:
                        val = float(item.text())
                        if val > max_val:
                            max_val = val
                            max_row = row
                    except ValueError:
                        continue  # Skip non-numeric cells

            # Highlight the max cell
            if max_row != -1 and max_val != 0:
                table.item(max_row, col).setBackground(QColor(255, 0, 0))  # Red


   