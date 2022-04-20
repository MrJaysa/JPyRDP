from socketio        import Client
from PyQt5.QtCore    import pyqtSlot, pyqtSignal, QThread
from pickle          import loads
from Main.Components import Pickable

class SocketProcess(QThread):
    stream_start       = pyqtSignal(dict)
    stream_err         = pyqtSignal(str)
    stream_connect     = pyqtSignal(str)
    stream_connect_err = pyqtSignal(str)
    stream_disconnect  = pyqtSignal()
    stream_image       = pyqtSignal(dict)

    stream_connect_user = pyqtSignal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        
    def run(self):
        try:
            import pyautogui
            self.sio = Client()

            @self.sio.on('connect')
            def on_connect():
                self.sio.send({
                    'id':   self.uid,
                    'type': 'client'
                })

                
            @self.sio.on('connect_error')
            def on_connect_error(data):
                pass
                # self.

            @self.sio.on('disconnect')trigger_desktop
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
                    self.desktop_user = msg.get('user')
                    self.stream_connect.emit(msg.get('msg'))
                    self.sio.emit('trigger_desktop', {
                        "user": self.desktop_user
                        "dimension": self.dimension
                    })

                else:
                    self.stream_connect_user.emit(msg.get('msg'))

            @self.sio.on('img_stream')
            def streamed_data(data):
                self.stream_image.emit(loads(data))

            self.sio.connect(self.url)
        
        except Exception as err:
            self.stream_err.emit(str(err))

    def set_credentials(self, url, uid):
        self.url = url
        self.uid = uid

    def connect_users(self, rid, pwd, dimensions):
        self.dimension = dimensions
        self.sio.emit('connect_users', {
            'id':  rid,
            'pwd': pwd
        })

    def on_positionChanged(self, data):
        pass

    def on_scroll(self, data):
        pass

    def on_click(self, data):
        pass

    def on_release(self, data):
        pass
