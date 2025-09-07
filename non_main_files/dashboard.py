import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QSpacerItem,QAction
)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime

from Layouts import MyWindow


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
    border: 1px solid black;
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



class Dashboard(MyWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production Analyser Dashboard")
        self.setGeometry(200, 100, 950, 600)
        self.setStyleSheet("background-color: #f5f7fa;")

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        menu_bar = self.menuBar() 
        menu_bar.setStyleSheet(qss)

        # Cycle Time Menu
        cycle_menu = menu_bar.addMenu("Cycle Time")

        self.view_cycle_action = QAction("Veiw Backup Cycle Time Data", self)
        cycle_menu.addAction(self.view_cycle_action)

        self.set_cycle_action = QAction("Veiw Current Cycle Time Data", self)
        cycle_menu.addAction(self.set_cycle_action)

        # Fault Delay Menu
        fault_menu = menu_bar.addMenu("Fault Delay")

        self.view_fault_action = QAction("View Fault Delay (Current)", self)
        self.view_fault_action.triggered.connect(
            lambda: self.label.setText("View Fault Delay (Backup)")  # Placeholder action
        )
        fault_menu.addAction(self.view_fault_action)

        self.configure_fault_action = QAction("View Fault Delay (Backup)", self)
        self.configure_fault_action.triggered.connect(
            lambda: self.label.setText("Configuring Fault Delay")
        )
        fault_menu.addAction(self.configure_fault_action)

        bcktime_menu = menu_bar.addMenu("Backup Time")

        self.set_backup_time = QAction("Set New Backup Time", self)
        self.set_backup_time.triggered.connect(
            lambda: self.dlg.show() # Placeholder action
        )
        bcktime_menu.addAction(self.set_backup_time)

        self.get_backup_time = QAction("Show Saved Backup Time", self)
        self.get_backup_time.triggered.connect(
            lambda: self.label.setText("Get Backup Time")  # Placeholder action
        )
        bcktime_menu.addAction(self.get_backup_time)

        main_layout = QVBoxLayout(central_widget)
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
        text_label = QLabel("Production Analyser")
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
        self.datetime_label.setStyleSheet("color: #37474f; margin-bottom: 10px;")
        self.datetime_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.datetime_label)
        self.update_datetime()
        timer = QTimer(self)
        timer.timeout.connect(self.update_datetime)
        timer.start(1000)

        # Summary Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignCenter)

        cards_layout.addWidget(self.create_summary_card("Today's Production", "1,250", "#002A4D"))
        cards_layout.addWidget(self.create_summary_card("Total Delay (min)", "32", "#002A4D"))
        cards_layout.addWidget(self.create_summary_card("Station Faults", "5", "#002A4D"))
        cards_layout.addWidget(self.create_summary_card("Efficiency (%)", "96.4", "#002A4D"))

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

    def create_summary_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"background:#C6E5F5; border-radius: 12px; border: 1px solid {color};")
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        label_title = QLabel(title)
        label_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        label_title.setStyleSheet(f"color: {color}; border: none;")
        label_title.setAlignment(Qt.AlignCenter)
        label_value = QLabel(value)
        label_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        label_value.setStyleSheet(f"color: {color}; border: none;")
        label_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_title)
        layout.addWidget(label_value)
        card.setFixedSize(180, 90)
        return card

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.datetime_label.setText(now.toString("dddd, dd MMMM yyyy - hh:mm:ss AP"))

def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()