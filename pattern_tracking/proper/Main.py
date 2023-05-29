import sys
from threading import Event

from PySide6.QtWidgets import QApplication

from pattern_tracking.proper.VideoReader import VideoReader
from pattern_tracking.proper.qt_gui.AppMainWindow import AppMainWindow


class Main:
    """
    Launches all separate operations on their own thread,
    the main thread will launch Qt's user interface.
    """

    def __init__(self):
        self._app = QApplication(sys.argv)
        """Qt GUI application object"""
        self._halt_event = Event()
        """Event used to halt operations on separate threads. Should only be modified by the Qt aboutToQuit() signal"""
        # self._operations_linker = OperationsLinker()  # TODO
        """Connects the widgets and the children threads together"""
        self._live_feed = VideoReader(0, False, self._halt_event)
        """Continuously reads the current video stream"""
        self._main_window = AppMainWindow()
        """QT Main window object"""

        self._app.aboutToQuit.connect(self._stop_children_operations)
        """Allows us to do properly stop children threads before the Qt interface exits"""

    def run(self):
        self._live_feed.run_threaded()
        self._main_window.show()
        self._app.exec()

    def _stop_children_operations(self):
        print("stopping")
        self._halt_event.set()


if __name__ == '__main__':
    worker = Main()
    worker.run()
