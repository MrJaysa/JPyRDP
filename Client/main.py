from PyQt5.QtWidgets          import QApplication
from sys                      import argv
from Main import Ui

if __name__ == '__main__':
    app=QApplication(argv)
    window = Ui(app)
    window.showFullScreen()
    app.exec_()