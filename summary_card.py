import os
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

class SummaryCard():
    def __init__(self, title, value, color):
        self.card = QFrame()
        self.card.setFrameShape(QFrame.StyledPanel)
        self.card.setStyleSheet(f"background:#C6E5F5; border-radius: 8px; border: 1px solid {color};")
        self.layout = QVBoxLayout(self.card)
        self.layout.setAlignment(Qt.AlignCenter)
        self.label_title = QLabel(title)
        self.label_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.label_title.setStyleSheet(f"color: {color}; border: none;")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_value = QLabel(value)
        self.label_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.label_value.setStyleSheet(f"color: {color}; border: none;")
        self.label_value.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_title)
        self.layout.addWidget(self.label_value)
        self.card.setFixedSize(180, 90)
    
    def update_value(self,updated_value):
        self.label_value.setText(updated_value)
    
    def show(self,layout):
        layout.addWidget(self.card)

    def get_card(self):
        return self.card
