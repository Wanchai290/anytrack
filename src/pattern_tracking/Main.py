import sys
from threading import Event

from PySide6.QtWidgets import QApplication

from src.pattern_tracking.logic.BackgroundComputation import BackgroundComputation
from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.logic.video.DummyVideoFeed import DummyVideoFeed
from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.AppMainWindow import AppMainWindow


class Main:
    """
    Launches all separate operations on their own thread,
    the main thread will launch Qt's user interface.
    """

    def __init__(self):
        self._app = QApplication(sys.argv)
        """Qt GUI application object"""
        self._global_halt = Event()
        """Event used to halt operations on separate threads. Should only be modified by the Qt aboutToQuit() signal"""
        self._tracker_manager = TrackerManager()
        """Contains all current trackers used"""
        self._live_feed_wrapper: LiveFeedWrapper = LiveFeedWrapper(DummyVideoFeed(self._global_halt))
        """Continuously reads the current video stream. Dummy feed on startup, replaced by a proper one by the user"""
        self._main_window = AppMainWindow(self._tracker_manager, self._live_feed_wrapper)
        """QT Main window object"""
        self._app.aboutToQuit.connect(self._stop_children_operations)
        """Allows us to do properly stop children threads before the Qt interface exits"""
        self._background_computation_worker = BackgroundComputation(
            self._tracker_manager,
            self._live_feed_wrapper,
            self._main_window.get_frame_display_widget(),
            self._main_window.get_plot_container_widget(),
            self._global_halt
        )
        """Connects the widgets and the children threads together"""

    def run(self):
        self._live_feed_wrapper.start()
        self._background_computation_worker.start()
        self._main_window.show()
        self._app.exec()

    def _stop_children_operations(self):
        self._global_halt.set()


if __name__ == '__main__':
    worker = Main()
    worker.run()
