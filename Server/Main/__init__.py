from PyQt5.QtWidgets          import QMainWindow, QMessageBox, QAction
from PyQt5.uic                import loadUi
from PyQt5.QtCore    import QObject, pyqtSlot, pyqtSignal, Qt, QFileSystemWatcher

from json            import load as json_loader, dump as json_dumper
from Main.ServerProcess  import Server_Thread
from Main.NetworkManager import ip_checker

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        loadUi('Main/Ui/main.ui', self)
        self.server_state = False
        self.observe_document()
        self.toggle_server.clicked.connect(self.start_server)
        self.url.setVisible(False)

    def read_observed_files(self):
        with open('Main/Observed/sock.json') as file:
            return json_loader(file)

    def observe_document(self):
        self.pathsobserved = ['Main/Observed/sock.json']
        self.fs_watcher = QFileSystemWatcher(self.pathsobserved)
        self.fs_watcher.fileChanged.connect(self.fileChangedEvent)

    def set_counts(self):
        try:
            content = self.read_observed_files()
            self.controller_count.setText(str(content.get('controller')) if content.get('controller') else '0')
            self.active_count.setText(str(content.get('active')) if content.get('active') else '0') 
            self.dev_count.setText(str(content.get('device')) if content.get('device') else '0')
        except:
            pass

    def fileChangedEvent(self, path):
        self.set_counts()

    def start_server(self):
        check_ip = ip_checker()
        if self.toggle_server.isChecked() and check_ip.get('status'):
            self.status.setText('Server Status: ON')
            self.url.setText(f'Server is active, your connection url is: <font color="cyan">http://{check_ip.get("host")}:5000</font>')
            self.sock_server = Server_Thread(self)
            self.sock_server.start()
            self.server_state = True
            self.url.setVisible(True)
        
        elif not self.toggle_server.isChecked() and check_ip.get('status'):
            self.toggle_server.setChecked(False)
            self.status.setText('Server Status: <font color="red">OFF</font>')
            if self.server_state:
                self.sock_server.thread.terminate()
                self.clear_observed()

            self.url.setText(f'Server is turned off successfully!')
            self.url.setVisible(True)
            
        else:
            self.toggle_server.setChecked(False)
            self.status.setText('Server Status: OFF')
            self.url.setText("<font color='black'>Please connect your device to either a hotspot, wireless or wired connection for network connectivity</font>")
            self.url.setVisible(True)

    def alertBox(self, alert, title, color, msg, size=2):
        alert = QMessageBox()
        alert.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        alert.setIcon(QMessageBox.Information if 'info' else QMessageBox.Warning if 'warning' else QMessageBox.Question if 'question' else QMessageBox.Critical)
        alert.setWindowTitle(title)
        alert.setText(f"<font size='{size}' color='{color}'>{msg}</font>")
        alert.exec()

    def closeEvent(self, event):
        # tying loose ends
        if self.server_state:
            self.sock_server.thread.terminate()

        self.clear_observed()

        print("closed")

    def clear_observed(self):
        with open('Main/Observed/sock.json', "w") as file:
            json_dumper({
                "controller": 0,
                "active": 0,
                "device": 0
            }, file, indent=4)
        
   