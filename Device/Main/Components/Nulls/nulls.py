from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QMovie
from PyQt5.uic       import loadUi
from PyQt5.QtCore    import pyqtSlot, pyqtSignal, QByteArray

class User_null(QWidget):
    def __init__(self, parent=None):
        super(User_null, self).__init__(parent)
        loadUi('Main/Ui/user_null.ui', self)

        self.gif_loader = QMovie('Main/Resources/loader.gif', QByteArray(), self)
        self.gif_loader.setCacheMode(QMovie.CacheAll)
        self.null_loader.setMovie(self.gif_loader)
        self.null_loader.setScaledContents(True)
        self.start_loader()
        self.setVisible(False)

    def start_loader(self):
        self.gif_status = True
        self.gif_loader.start()
        self.gif_loader.setSpeed(200)

    def stop_loader(self):
        self.gif_status = False
        self.movie.stop()

    def toggle_visibility(self, toggle):
        self.setVisible(toggle)