from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from menu import Menu
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 400, 300)

        self.button = QPushButton("Click for Menu", self)
        self.button.setGeometry(150, 130, 120, 40)

        # Pass button to menu handler
        self.menu_handler = Menu(self.button)
        self.menu_handler.add_menuItem("Option A", lambda: print("Option A selected"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
