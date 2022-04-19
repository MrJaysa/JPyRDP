from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui     import QMovie
from PyQt5.uic       import loadUi
from PyQt5.QtCore    import QByteArray, Qt

class Ui_Loader(QDialog):
    def __init__(self, parent=None):
        super(Ui_Loader, self).__init__(parent)
        loadUi('Main/Ui/loader.ui', self)
        self.setWindowFlags( Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint )

        self.gif_loader = QMovie('Main/Resources/loader.gif', QByteArray(), self)
        self.gif_loader.setCacheMode(QMovie.CacheAll)
        self.loader_label.setMovie(self.gif_loader)
        self.loader_label.setScaledContents(True)
        self.gif_status = True
        self.gif_loader.start()
        self.gif_loader.setSpeed(200)
        self.close()