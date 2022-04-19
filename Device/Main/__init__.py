from PyQt5.QtWidgets          import QMainWindow, QMessageBox
from PyQt5.uic                import loadUi
from PyQt5.QtCore    import QObject, pyqtSlot, pyqtSignal, Qt, QThread
from sys             import argv
from os.path         import abspath, join, dirname
from base64          import b64encode
from validators      import url as url_validator

from Main.Components        import User_null, Ui_Loader
from Main.SocketProcess     import SocketProcess

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        loadUi('Main/Ui/main.ui', self)
        # loader class
        self.loader_modal = Ui_Loader(self)
        # socket class
        self.socket_client = SocketProcess(self)
        # second screen items
        self.await_user = User_null(self)
        self.await_user.toggle_visibility(False)
        self.user_layout.addWidget(self.await_user)

        # setups
        self.views.setCurrentIndex(0)
        self.system_events()
        self.hide_elements()

        self.setWindowFlags( Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint )

    def system_events(self):
        self.btn_submit.clicked.connect(self.start_stream)
        self.uid.textChanged.connect(self.input_edited)
        self.url.textChanged.connect(self.input_edited)
        self.pwd.textChanged.connect(self.input_edited)

    def hide_elements(self):
        self.main_flash.setVisible(False)

    def input_edited(self):
        if self.main_flash.isVisible():
            self.main_flash.setVisible(False)


    def start_stream(self):
        if self.uid.text() and self.url.text() and self.pwd.text():
            if url_validator(self.url.text()):
                self.loader_modal.show()
                self.socket_client.set_credentials(self.url.text(), self.uid.text(), self.pwd.text())
                
                self.socket_client.start()
                self.socket_client.stream_start.connect(self.stream_transmission)
                self.socket_client.stream_err.connect(self.stream_error)
                self.socket_client.stream_connect_err.connect(self.stream_connect_err)
                self.socket_client.stream_connect.connect(self.stream_connect)
                self.input_deactivate(False)
            else:
                self.main_flash.setText('Please enter a valid URL')
                self.main_flash.setVisible(True)


        else:
            self.main_flash.setText('Please fill the forms fields provided.')
            self.main_flash.setVisible(True)
            self.input_deactivate(True)
    
    @pyqtSlot(dict)
    def stream_transmission(self, val):
        self.loader_modal.close()
        self.views.setCurrentIndex(1)
        self.main_page.setVisible(False)
        self.await_user.dev_rid.setText(self.uid.text())
        self.await_user.dev_password.setText(self.pwd.text())

        self.await_user.start_loader()
        self.await_user.toggle_visibility(True)

    @pyqtSlot(str)
    def stream_error(self, err):
        self.loader_modal.close()
        self.main_flash.setText(err)
        self.main_flash.setVisible(True)
        self._alertBox(
            alert = 'info', 
            title = 'Invalid URL', 
            color = '#3a93ff',
            msg   = 'Please Check the URL provided and try again',
            func  = self.input_deactivate
        )
        self.input_deactivate(True)
    
    @pyqtSlot(str)
    def stream_connect_err(self, err):
        self.loader_modal.close()
        self.main_flash.setText(err)
        self.main_flash.setVisible(True)
        if self.socket_client.isRunning():
            self.socket_client.terminate()
        self.input_deactivate(True)

    @pyqtSlot(str)
    def stream_connect(self, msg):
        self.await_user.null_info.setText(msg)

    def _alertBox(self, alert, title, color, msg, size=2, func=None):
        if func:
            func(False)

        def close_alert():
            _.close()
            func(True)
            
        _ = QMessageBox(self)
        _.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        _.setIcon(QMessageBox.Information if 'info' else QMessageBox.Warning if 'warning' else QMessageBox.Question if 'question' else QMessageBox.Critical)
        _.setWindowTitle(title)
        _.setText(f"<font size='{size}' color='{color}'>{msg}</font>")
        _.buttonClicked.connect(lambda:close_alert())
        _.exec()
        

    def input_deactivate(self, param):
        self.url.setEnabled(param)
        self.uid.setEnabled(param)
        self.pwd.setEnabled(param)
        self.btn_submit.setEnabled(param)

    def closeEvent(self, event):
        if self.socket_client.isRunning():
            self.socket_client.terminate()
        print("closed")
