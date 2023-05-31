from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import QMainWindow, QMenu, QWidget

from pattern_tracking.proper.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.CreateTrackerAction import CreateTrackerAction
from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.TrackersMenu import TrackersMenu
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager
from pattern_tracking.proper.qt_gui.FrameDisplayWidget import FrameDisplayWidget


class AppMainWindow(QMainWindow):
    """
    Main display to the user. Initializes the application
    with the different menus, sidebar menus and buttons
    """

    def __init__(self, tracker_manager: TrackerManager, frame_shape: tuple[int, int, int]):
        super().__init__()
        self._TRACKER_MANAGER = tracker_manager
        self._FRAME_DISPLAY = FrameDisplayWidget(tracker_manager, frame_shape)
        self._LIVE_DISTANCE_PLOT = LivePlotterDockWidget(self)
        self._TRACKERS_MENU = TrackersMenu(tracker_manager, parent=self)

        self.menuBar().addMenu(self._TRACKERS_MENU)
        self.addDockWidget(Qt.RightDockWidgetArea, self._LIVE_DISTANCE_PLOT)
        self.setCentralWidget(self._FRAME_DISPLAY)

    def get_frame_display_widget(self) -> FrameDisplayWidget:
        return self._FRAME_DISPLAY
