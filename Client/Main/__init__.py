from PyQt5.QtWidgets          import QMainWindow, QMessageBox
from PyQt5.uic                import loadUi
# from PyQt5.QtGui     import QPixmap
from PyQt5.QtCore    import QObject, pyqtSlot, pyqtSignal, Qt, QThread
from sys             import argv
from os.path         import abspath, join, dirname
from base64          import b64encode
from validators      import url as url_validator

from Main.Components         import User, User_null, Ui_Loader
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
        self.user_available = User(self)
        self.await_user.toggle_visibility(False)
        self.user_available.toggle_visibility(False)
        self.user_layout.addWidget(self.await_user)
        self.user_layout.addWidget(self.user_available)

        # setup
        self.views.setCurrentIndex(0)
        self.system_events()
        self.hide_elements()




        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags( Qt.WindowCloseButtonHint)
        # self.setWindowFlags( Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint )

    def system_events(self):
        self.btn_submit.clicked.connect(self.start_stream)
        self.uid.textChanged.connect(self.input_edited)
        self.url.textChanged.connect(self.input_edited)
        
        self.user_available.dev_id.textChanged.connect(self.user_component_edit)
        self.user_available.dev_pwd.textChanged.connect(self.user_component_edit)
        self.user_available.connect_client.clicked.connect(self.user_connect)
        self.socket_client.stream_connect_user.connect(self.stream_connect_user)
    
    def user_component_edit(self):
        if self.user_available.user_alert.isVisible():
            self.user_available.user_alert.setVisible(False)
    
    def toggle_user_component_input(self, param):
        self.user_available.dev_id.setEnabled(param)
        self.user_available.dev_pwd.setEnabled(param)
        self.user_available.connect_client.setEnabled(param)

    
    def user_connect(self):
        if self.user_available.dev_id.text() and self.user_available.dev_pwd.text():
            self.toggle_user_component_input(False)
            self.loader_modal.show()
            self.socket_client.connect_users(self.user_available.dev_id.text(), self.user_available.dev_pwd.text())
        else:
            self.user_available.user_alert.setText('Please fill the form fields provided.')
            self.user_available.user_alert.setVisible(True)
            self.toggle_user_component_input(True)

    def hide_elements(self):
        self.main_flash.setVisible(False)

    def input_edited(self):
        if self.main_flash.isVisible():
            self.main_flash.setVisible(False)


    def start_stream(self):
        if self.uid.text() and self.url.text():
            if url_validator(self.url.text()):
                self.loader_modal.show()
                self.socket_client.set_credentials(self.url.text(), self.uid.text())
                
                self.socket_client.start()
                self.socket_client.stream_start.connect(self.stream_transmission)
                self.socket_client.stream_err.connect(self.stream_error)
                self.socket_client.stream_connect_err.connect(self.stream_connect_err)
                self.socket_client.stream_connect.connect(self.stream_connect)
                self.socket_client.stream_image.connect(self.load_image)
                self.input_deactivate(False)
            else:
                self.main_flash.setText('Please enter a valid URL.')
                self.main_flash.setVisible(True)


        else:
            # make a flash method to handle this
            self.main_flash.setText('Please fill the form fields provided.')
            self.main_flash.setVisible(True)
            self.btn_submit.setEnabled(True)
    
    @pyqtSlot(dict)
    def stream_transmission(self, val):
        self.loader_modal.close()
        self.views.setCurrentIndex(1)
        self.main_page.setVisible(False)

        if val.get('user'):
            if self.await_user.gif_status:
                self.await_user.stop_loader()
            if self.await_user.isVisible():
                self.await_user.toggle_visibility(False)
            if self.user_available.isVisible() == False:
                self.user_available.toggle_visibility(True)
                
            self.user_available.count_dev.setText(f'Devices: {len(val.get("user"))}')

        else:
            self.await_user.start_loader()
            self.user_available.toggle_visibility(False)
            self.await_user.toggle_visibility(True)
            
    
    @pyqtSlot(str)
    def stream_error(self, err):
        self.loader_modal.close()
        self.main_flash.setText(err)
        self.main_flash.setVisible(True)
        self.alertBox(
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
    def stream_connect_user(self, msg):
        self.loader_modal.close()
        self.user_available.user_alert.setText(msg)
        self.user_available.user_alert.setVisible(True)
        self.toggle_user_component_input(True)
        
    @pyqtSlot(str)
    def stream_connect(self, msg):
        self.loader_modal.close()
        self.user_available.user_alert.setText(msg)
        self.user_available.user_alert.setVisible(True)
        # create a new view in the ui and add a view for showing the image
        self.views.setCurrentIndex(2)
        self.await_user.toggle_visibility(False)
        self.user_available.toggle_visibility(False)

    @pyqtSlot(dict)
    def load_image(self, img):
        self.rdp_img.setPixmap(img['image'])
        
    def alertBox(self, alert, title, color, msg, size=2, func=None):
        if func:
            func(False)

        def close_alert():
            alert.close()
            
        alert = QMessageBox(self)
        alert.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        alert.setIcon(QMessageBox.Information if 'info' else QMessageBox.Warning if 'warning' else QMessageBox.Question if 'question' else QMessageBox.Critical)
        alert.setWindowTitle(title)
        alert.setText(f"<font size='{size}' color='{color}'>{msg}</font>")
        alert.buttonClicked.connect(close_alert)
        alert.exec()
        if func:
            func(True)

    def input_deactivate(self, param):
        self.url.setEnabled(param)
        self.uid.setEnabled(param)
        self.btn_submit.setEnabled(param)

    def closeEvent(self, event):
        if self.socket_client.isRunning():
            self.socket_client.terminate()
        print("closed")
