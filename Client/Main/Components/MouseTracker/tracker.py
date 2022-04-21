from PyQt5.QtCore import QObject, pyqtSignal, QEvent

class MouseTracker(QObject):
    mousePosition   = pyqtSignal(int, int)
    mouseScroll     = pyqtSignal(int, int)
    mouseClick      = pyqtSignal(int)
    mouseRelease    = pyqtSignal(int)

    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self):
        return self._widget

    def eventFilter(self, obj, event):
        if obj is self.widget:
            if event.type() == QEvent.MouseMove:
                self.mousePosition.emit(event.pos().x(), event.pos().y())

            if event.type() == QEvent.MouseButtonPress:
                self.mouseClick.emit(event.button())

            if event.type() == QEvent.MouseButtonRelease:
                self.mouseRelease.emit(event.button())

            if event.type() == QEvent.Wheel:
                self.mouseScroll.emit(event.angleDelta().x(), event.pos().y())

        return super().eventFilter(obj, event)
