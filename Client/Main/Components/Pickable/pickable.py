from PyQt5.QtCore    import QIODevice, QByteArray, QDataStream
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