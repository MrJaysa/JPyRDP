from PyQt5.QtCore import QThread
from multiprocessing import Process
from Main.Server_Main import socket as socketio, app

class Start_Server(Process):
    def __init__(self):
        super(Start_Server, self).__init__()

    def run(self):
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)

class Server_Thread(QThread, Process):
    def __init__(self, port, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        self.thread = Start_Server()
        self.thread.start()