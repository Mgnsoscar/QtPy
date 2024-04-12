from backend import Backend
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == "__main__":

    application = QApplication(sys.argv)
    ja = Backend()
    #ja.database_handler.add_user("Jakob")
    #ja.database_handler.add_user("Finn Christian")
    #ja.database_handler.add_user("Martin")
    ja.show()
    sys.exit(application.exec_())