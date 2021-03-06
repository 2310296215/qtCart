from multiprocessing.spawn import freeze_support
import sys
from PyQt5.QtWidgets import QApplication
from Controller import MainController
from View import ViewWindow
import multiprocessing as mp

if __name__ == "__main__":
    mp.freeze_support()
    app = QApplication(sys.argv)
    c = MainController(ViewWindow())
    c.start()
    sys.exit(app.exec())
