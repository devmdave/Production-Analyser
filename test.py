import sys
import random
import psutil
import json
import time
import threading
from datetime import datetime, timedelta
from Layouts import MyWindow
from MockPLCServer.mock_plc import pycomm3
from my_plc import Plc
from PyQt5.QtCore import Qt, QTimer, QTime, QDateTime, QStringListModel
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QBrush, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QFrame, QPushButton, QSizePolicy, QMenu, QAction, QWidget,
    QTableWidget, QTableWidgetItem, QLineEdit, QListView, QProgressDialog, QTimeEdit, QMessageBox, QSpacerItem
)

from TagManager import TagManagerWindow
from Dialog import *
import os
import pandas as pd
import my_plc
import time
from summary_card import SummaryCard
from PyQt5.QtCore import QThread, pyqtSignal

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




class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_activated_once = False
        self.initialise_dashboard()
    
    def initialise_dashboard(self):
        self.setWindowTitle("Professional Dashboard")
        self.setWindowIcon(QIcon.fromTheme("applications-system"))
        self.resize(850, 520)
       

        self.plc = pycomm3()

        self.dark_mode = False
        self.setStyleSheet(self._get_stylesheet())

        self.menu_bar = self.menuBar()

        self.active_dashboard = True
        self.setWindowTitle("Production Analyser")
        self.setFixedSize(1200,600)
        self.setGeometry(100, 100, 1200, 600)
        self.setWindowIcon(QIcon("icon.png"))
        self.cycle_time = 0
        self.file_path = "production.xlsx"
        self.Dialog = Dialog()
        self.dlg = BackupTimeDialog()
        self.edit_cyctime_win = TagManagerWindow(json_path="plc_custom_user_tags\\cycle_time_tags.json")
        self.edit_fault_delay_win = TagManagerWindow(json_path="plc_custom_user_tags\\station_fault_tags.json")
        self.edit_station_fault_win = TagManagerWindow(json_path="plc_custom_user_tags\\fault_delay_tags.json")
        self.edit_tip_dress_win = TagManagerWindow(json_path="plc_custom_user_tags\\tip_dress_tags.json")
        self.edit_tip_change_win = TagManagerWindow(json_path="plc_custom_user_tags\\tip_dress_tags.json")
        self.edit_dashboard_win = TagManagerWindow(json_path="plc_custom_user_tags\\dashboard_tags.json")
        self.label = QLabel()

        self.last_backup_time = datetime.now() - timedelta(hours=2, minutes=15)
        self.plc_connected = False

        # Store original window size for scaling
        self.original_size = (850, 520)
        self.original_fonts = {
            'heading': 24,
            'time': 22,
            'backup': 14,
            'plc': 14,
            'log_title': 18,
            'param_title': 12,
            'param_value': 22,
            'button': 10
        }

        self._init_ui()
        self._init_timers()
        self.param_thread = threading.Thread(target=self._update_parameters, daemon=True)
        self.param_thread.start()
        self._log("Dashboard initialized.")


    def _init_ui(self):
        try:
            self.central_widget.destroy()
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
        except Exception as e:
            pass
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        if self.ui_activated_once == False:
            self._create_menu_bar()
            self.ui_activated_once = True

        # Top header with logo and heading
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setAlignment(Qt.AlignLeft)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("logo.PNG")
        logo_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio))
        header_layout.addWidget(logo_label)

        # Right side: main heading and subheading
        right_layout = QVBoxLayout()
        right_layout.setSpacing(2)

        # Main heading
        heading = QLabel("Production Analyser")
        heading.setFont(QFont("Segoe UI", 20, QFont.Bold))
        heading.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(heading)

        # Subheading
        subheading = QLabel("Real Time Metrics")
        subheading.setFont(QFont("Segoe UI", 10))
        subheading.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(subheading)

        header_layout.addLayout(right_layout)

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Top info panel
        info_panel = QHBoxLayout()
        info_panel.setSpacing(15)

        # O.E.E (%)
        self.oee_label = QLabel("0.0")
        self.oee_label.setFont(QFont("Segoe UI", 15))
        self.oee_label.setAlignment(Qt.AlignCenter)
        self.oee_label.setFixedWidth(220)
        oee_box = self._create_info_box("O.E.E (%)", self.oee_label)
        oee_box.setFixedWidth(250)
        info_panel.addWidget(oee_box)

        # Current Time
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFixedWidth(220)
        time_box = self._create_info_box("Current Time", self.time_label)
        time_box.setFixedWidth(250)
        info_panel.addWidget(time_box)

        # Last Backup Time
        self.backup_label = QLabel()
        self.backup_label.setFont(QFont("Segoe UI", 15))
        self.backup_label.setAlignment(Qt.AlignCenter)
        self.backup_label.setFixedWidth(220)
        backup_box = self._create_info_box("Last Backup", self.backup_label)
        backup_box.setFixedWidth(250)
        info_panel.addWidget(backup_box)

        # PLC Connection Status
        plc_status_layout = QHBoxLayout()
        plc_status_layout.setAlignment(Qt.AlignCenter)
        self.plc_status_label = QLabel("Disconnected")
        self.plc_status_label.setFont(QFont("Segoe UI", 14))
        self.plc_status_label.setStyleSheet("color: white; background-color: #FF0000; border-radius: 0px; padding: 4px 8px;")
        plc_status_layout.addWidget(self.plc_status_label)
        plc_status_widget = QWidget()
        plc_status_widget.setLayout(plc_status_layout)
        info_panel.addWidget(self._create_info_box("PLC Connection", plc_status_widget))

        # Light/Dark Mode Toggle Button moved to log section

        main_layout.addLayout(info_panel)

        # Bottom layout: Four parameter frames + Log window
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(15)

        # Four parameter frames
        params_widget = QWidget()
        params_layout = QGridLayout()
        params_layout.setSpacing(15)

        # Create parameter frames
        self.param_labels = {}

        # Load parameters from JSON
        with open('config.json', 'r') as f:
            data = json.load(f)
        param_names = [p['name'] for p in data.get('parameters', [])]
        for i, name in enumerate(param_names):
            label_value = QLabel("0")
            label_value.setFont(QFont("Segoe UI", 22, QFont.Bold))
            label_value.setAlignment(Qt.AlignCenter)
            label_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            frame = self._create_info_box(name, label_value)
            # frame.setMinimumSize(180, 110)
            params_layout.addWidget(frame, i // 4, i % 4)
            self.param_labels[name] = label_value

        params_widget.setLayout(params_layout)
        bottom_layout.addWidget(params_widget)

        # Log window
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(5)

        log_title = QLabel("Events")
        log_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        log_title.setAlignment(Qt.AlignLeft)
        log_layout.addWidget(log_title)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)

        # Add a clear log button
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.setFixedWidth(100)
        clear_log_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        clear_log_btn.clicked.connect(self.log_text.clear)
        buttons_layout.addWidget(clear_log_btn)

        # Light/Dark Mode Toggle Button moved here for smoother functioning
        self.mode_toggle_btn = QPushButton("Switch to Light Mode")
        self.mode_toggle_btn.setFixedSize(180, 36)
        self.mode_toggle_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.mode_toggle_btn.clicked.connect(self._toggle_mode)
        buttons_layout.addWidget(self.mode_toggle_btn)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        log_layout.addWidget(buttons_widget, alignment=Qt.AlignRight)

        log_widget.setLayout(log_layout)
        bottom_layout.addWidget(log_widget)

        main_layout.addLayout(bottom_layout)

    def _init_timers(self):
        # Update current time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()

        # Update backup time every minute (simulate)
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self._update_backup_time)
        self.backup_timer.start(60000)
        self._update_backup_time()

        # Update PLC connection status every 5 seconds (simulate)
        self.plc_timer = QTimer()
        self.plc_timer.timeout.connect(self._update_plc_status)
        self.plc_timer.start(5000)
        self._update_plc_status()

    def _update_time(self):
        now = QTime.currentTime()
        self.time_label.setText(now.toString("hh:mm:ss AP"))
        # Log every minute
        if now.second() == 0:
            self._log(f"Time updated: {now.toString('hh:mm:ss AP')}")

    def _update_backup_time(self):
        try:
            elapsed = datetime.now() - self.last_backup_time
            hours, remainder = divmod(elapsed.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            self.backup_label.setText(f"{hours}h {minutes}m ago")
        except Exception as e:
            pass

    def _update_plc_status(self):
        try:
            self.plc_connected = not self.plc_connected
            if self.plc_connected:
                self.plc_status_label.setText("Connected")
                self.plc_status_label.setStyleSheet("color: white; background-color: #008000; border-radius: 0px; padding: 4px 8px;")
                self._log("PLC connected.")
            else:
                self.plc_status_label.setText("Disconnected")
                self.plc_status_label.setStyleSheet("color: white; background-color: #FF0000; border-radius: 0px; padding: 4px 8px;")
                self._log("PLC disconnected.")
        except Exception as e:
            pass

    def _update_parameters(self):
        while True:
            plc_res = self.plc.read_dashboard_tags()
            # Update parameter values from JSON or simulate if no value provided
            with open('config.json', 'r') as f:
                data = json.load(f)
            parameters = data.get('parameters', [])
            for param in parameters:
                name = param.get('name')
                if name in self.param_labels:
                    self.param_labels[name].setText(str(plc_res[name]))

            # Simulate OEE update
            oee = random.uniform(50.0, 100.0)
            self.oee_label.setText(f"{oee:.1f}")

            self._log(f"Parameters updated from config.json, O.E.E={oee:.1f}%")
            time.sleep(60)

    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def _create_info_box(self, title, widget):
        box = QFrame()
        box.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(widget)
        box.setLayout(layout)
        return box

    def _create_menu_bar(self):
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
        self.view_cycle_action.triggered.connect(lambda: self.cycletime_backup_layout())
        # self.view_current_cycle_action.triggered.connect(lambda: self.cycletime_current_layout())

        self.set_backup_time = QAction("Set New Backup Time", self)
        self.set_backup_time.triggered.connect(lambda: self.dlg.show()) #Placeholder action
        
        setting_menu.addAction(self.set_backup_time)

        self.get_backup_time = QAction("Show Saved Backup Time", self)
        self.get_backup_time.triggered.connect(lambda: self.label.setText("Get Backup Time") ) # Placeholder action
                
        setting_menu.addAction(self.get_backup_time)

        self.edit_cycletime_tag_action.triggered.connect(lambda: self.edit_cycle_time_tags())
        self.edit_faultdelay_tag_action.triggered.connect(lambda: self.edit_fault_delay_tags())
        self.edit_stationfault_tag_action.triggered.connect(lambda: self.edit_fault_delay_tags())
        self.edit_tipchange_tag_action.triggered.connect(lambda: self.edit_tip_change_tags())
        self.edit_tipdress_tag_action.triggered.connect(lambda:self.edit_tip_dress_tags())
        self.edit_dashboard_tag_action.triggered.connect(lambda:self.edit_dashboard_tags())



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
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame {
                    background-color: #2c3e50;
                    border-radius: 10px;
                    padding: 3px;
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
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame {
                    background-color: #C6E5F5;
                    border-radius: 10px;
                    padding: 5px;
                }
            """

    def _toggle_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.mode_toggle_btn.setText("Switch to Light Mode")
        else:
            self.mode_toggle_btn.setText("Switch to Dark Mode")
        self.setStyleSheet(self._get_stylesheet())

    def edit_cycle_time_tags(self):
        self.edit_cyctime_win.show()

    def edit_station_fault_tags(self):
        self.edit_fault_delay_win.show()

    def edit_fault_delay_tags(self):
        self.edit_station_fault_win.show()

    def edit_tip_dress_tags(self):
        self.edit_tip_dress_win.show()

    def edit_tip_change_tags(self):
        self.edit_tip_change_win.show()

    def edit_dashboard_tags(self):
        self.edit_dashboard_win.show()

    def show_about_dialog(self):
        QMessageBox.about(self, "About", "Production Analyser\nVersion 1.0\nDeveloped by Your Name")


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
        back_button.clicked.connect(lambda : self.reinitialize_dashboard())

                                    

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
        today_str = datetime.now().strftime('%d-%m-%Y')
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

    def reinitialize_dashboard(self):
        self.initialise_dashboard()



def main():
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
