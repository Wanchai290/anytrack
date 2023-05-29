import sys
from threading import Event

from PySide6.QtWidgets import QApplication

from pattern_tracking.proper.BackgroundComputation import BackgroundComputation
from pattern_tracking.proper.TemplateTracker import TemplateTracker
from pattern_tracking.proper.TrackerManager import TrackerManager
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
        self._tracker_manager = TrackerManager()
        # >>> required before I make the menus to create them
        self._tracker_manager.add_tracker(TemplateTracker("Default"))
        self._tracker_manager.set_active_tracker("Default")
        # <<<
        """Contains all curren trackers used"""
        self._main_window = AppMainWindow(self._tracker_manager)
        """QT Main window object"""
        self._live_feed = VideoReader(0, False, self._halt_event)
        """Continuously reads the current video stream"""
        self._app.aboutToQuit.connect(self._stop_children_operations)
        """Allows us to do properly stop children threads before the Qt interface exits"""
        self._background_computation_worker = BackgroundComputation(
            self._tracker_manager,
            self._live_feed,
            self._main_window.get_frame_display_widget(),
            self._halt_event
        )
        """Connects the widgets and the children threads together"""

    def run(self):
        self._live_feed.run_threaded()
        self._background_computation_worker.run_threaded()
        self._main_window.show()
        self._app.exec()

    def _stop_children_operations(self):
        self._halt_event.set()


if __name__ == '__main__':
    worker = Main()
    worker.run()
