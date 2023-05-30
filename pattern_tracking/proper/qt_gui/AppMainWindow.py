from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import QMainWindow, QMenu

from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.TrackersMenuActions import TrackersMenuActions
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager
from pattern_tracking.proper.qt_gui.FrameDisplayWidget import FrameDisplayWidget


class AppMainWindow(QMainWindow):
    """
    Main display to the user. Initializes the application
    with the different menus, sidebar menus and buttons
    """

    DEFAULT_TRACKERS_MENUBAR_KEYWORD = "Trackers"

    def __init__(self, tracker_manager: TrackerManager, frame_shape: tuple[int, int, int]):
        super().__init__()

        self._TRACKER_MANAGER = tracker_manager
        self._FRAME_DISPLAY = FrameDisplayWidget(tracker_manager, frame_shape)
        # self._live_dist_plot: QWidget =

        # todo: somehow I can't create my custom QMenu and display it
        # so i have to create it in another way
        # this is dumb shit
        self._TRACKERS_MENU = self.menuBar().addMenu(AppMainWindow.DEFAULT_TRACKERS_MENUBAR_KEYWORD)
        self._TRACKERS_MENU_ACTIONS = TrackersMenuActions(tracker_manager)
        self._TRACKERS_MENU_ACTIONS.fill(self._TRACKERS_MENU)

        self.setCentralWidget(self._FRAME_DISPLAY)

    def get_frame_display_widget(self) -> FrameDisplayWidget:
        return self._FRAME_DISPLAY
