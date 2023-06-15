import sys
from threading import Event

from PySide6.QtWidgets import QApplication

from pattern_tracking.proper.logic.BackgroundComputation import BackgroundComputation
from pattern_tracking.proper.logic.tracker.TrackerManager import TrackerManager
from pattern_tracking.proper.logic.video.AbstractFrameProvider import AbstractFrameProvider
from pattern_tracking.proper.logic.video.LiveFeedWrapper import LiveFeedWrapper
from pattern_tracking.proper.logic.video.VideoReader import VideoReader
from pattern_tracking.proper.qt_gui.AppMainWindow import AppMainWindow
from pattern_tracking.proper.shared import utils


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
        """Contains all current trackers used"""
        _, working_ports, _ = utils.opencv_list_available_camera_ports()
        self._live_feed_wrapper: LiveFeedWrapper = LiveFeedWrapper(VideoReader(working_ports[0], False, self._halt_event))
        # self._live_feed: AbstractFrameProvider =
        """Continuously reads the current video stream"""
        self._main_window = AppMainWindow(self._tracker_manager, self._live_feed_wrapper)
        """QT Main window object"""
        self._app.aboutToQuit.connect(self._stop_children_operations)
        """Allows us to do properly stop children threads before the Qt interface exits"""
        self._background_computation_worker = BackgroundComputation(
            self._tracker_manager,
            self._live_feed_wrapper,
            self._main_window.get_frame_display_widget(),
            self._main_window.get_plot_container_widget(),
            self._halt_event
        )
        """Connects the widgets and the children threads together"""

    def run(self):
        self._live_feed_wrapper.start()
        self._background_computation_worker.start()
        self._main_window.show()
        self._app.exec()

    def _stop_children_operations(self):
        self._halt_event.set()


if __name__ == '__main__':
    worker = Main()
    worker.run()
