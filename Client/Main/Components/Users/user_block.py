from PyQt5.QtWidgets import QWidget
from PyQt5.uic                import loadUi

class User(QWidget):
    def __init__(self, parent=None):
        super(User, self).__init__(parent)
        loadUi('Main/Ui/user_block.ui', self)
        self.user_alert.setVisible(False)
        self.setVisible(False)
        
    def toggle_visibility(self, toggle):
        self.setVisible(toggle)