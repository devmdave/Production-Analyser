import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt

class Window1(QWidget):
    def __init__(self, navigate_to_window2):
        super().__init__()
        layout = QVBoxLayout()
        btn = QPushButton("Go to Window 2")
        btn.clicked.connect(navigate_to_window2)
        layout.addWidget(btn)
        self.setLayout(layout)

class Window2(QWidget):
    def __init__(self, navigate_back):
        super().__init__()
        layout = QVBoxLayout()

        # Header bar with back button
        header = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect( navigate_back)
        title = QLabel("Window 2")
        title.setAlignment(Qt.AlignCenter)

        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(title)
        header.addStretch()

        layout.addLayout(header)

        # Content
        content = QLabel("This is Window 2")
        content.setAlignment(Qt.AlignCenter)
        layout.addWidget(content)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navigation Example")
        self.setGeometry(100, 100, 400, 300)
        self.show_window1()

    def show_window1(self):
        self.window1 = Window1(self.show_window2)
        self.setCentralWidget(self.window1)

    def show_window2(self):
        self.window2 = Window2(self.show_window1)
        self.setCentralWidget(self.window2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
