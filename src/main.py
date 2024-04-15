from backend import Backend
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == "__main__":

    application = QApplication(sys.argv)
    ja = Backend()
    ja.show()
    sys.exit(application.exec_())