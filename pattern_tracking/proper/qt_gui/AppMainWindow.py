from PySide6.QtWidgets import QMainWindow, QWidget

from pattern_tracking.proper.TrackerManager import TrackerManager
from pattern_tracking.proper.qt_gui.FrameDisplayWidget import FrameDisplayWidget


class AppMainWindow(QMainWindow):
    """
    Main display to the user. Initializes the application
    with the different menus, sidebar menus and buttons
    """

    def __init__(self, tracker_manager: TrackerManager):
        super().__init__()

        self._FRAME_DISPLAY = FrameDisplayWidget(tracker_manager)
        # self._live_dist_plot: QWidget =

        self.setCentralWidget(self._FRAME_DISPLAY)

    def get_frame_display_widget(self) -> FrameDisplayWidget:
        return self._FRAME_DISPLAY
