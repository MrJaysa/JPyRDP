from PyQt5.QtWidgets          import QApplication
from sys                      import argv
from Main import Ui

if __name__ == '__main__':
    app=QApplication(argv)
    window = Ui()
    window.show()
    app.exec_()