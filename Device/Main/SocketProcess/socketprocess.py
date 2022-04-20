from socketio        import Client
from PyQt5.QtCore    import pyqtSlot, pyqtSignal, QThread, QIODevice, QByteArray, QDataStream
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui     import QScreen
from time            import sleep
from pickle          import dumps
from PyQt5.QtGui     import QPixmap

class Pickable(QPixmap):
    def __reduce__(self):
        return type(self), (), self.__getstate__()

    def __getstate__(self):
        ba = QByteArray()
        stream = QDataStream(ba, QIODevice.WriteOnly)
        stream << self
        return ba
    
    def __setstate__(self, ba):
        stream = QDataStream(ba, QIODevice.ReadOnly)
        stream >> self

class SocketProcess(QThread):
    stream_start       = pyqtSignal(dict)
    stream_err         = pyqtSignal(str)
    stream_connect     = pyqtSignal(str)
    stream_connect_err = pyqtSignal(str)
    stream_disconnect  = pyqtSignal()
    view               = QApplication([])

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        
    def run(self):
        try:
            self.sio = Client()

            @self.sio.on('connect')
            def on_connect():
                self.sio.send({
                    'id':   self.uid,
                    'type': 'desktop',
                    'pass': self.pwd
                })

                
            @self.sio.on('connect_error')
            def on_connect_error(data):
                pass

            @self.sio.on('disconnect')
            def on_disconnect():
                self.stream_disconnect.emit()

            @self.sio.on('message')
            def receive_custom(msg):
                if msg.get('status') == 200:
                    self.stream_start.emit(msg)

                else:
                    self.stream_connect_err.emit(msg.get('message'))

            @self.sio.on('establish_connection')
            def receive_custom(msg):
                if msg.get('status') == 200:
                    self.client_user = msg.get('user')
                    self.client_dimension = msg.get('dimension')
                    self.stream_connect.emit(msg.get('msg'))
                    self.start_streaming()

            
            self.sio.connect(self.url)
        
        except Exception as err:
            self.stream_err.emit(str(err))

    @pyqtSlot(str, str)
    def set_credentials(self, url, uid, pwd):
        self.url = url
        self.uid = uid
        self.pwd = pwd

    def start_streaming(self):
        # import pyautogui
        while True:
            sleep(0.33)
            self.sio.emit('streamer', {
                'data': dumps({
                    "image": Pickable(
                        QScreen.grabWindow(self.view.primaryScreen(), self.view.desktop().winId())
                    )
                }),
                'user': self.client_user
            })
