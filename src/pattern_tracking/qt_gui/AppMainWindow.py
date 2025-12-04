import threading

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QMainWindow

from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from src.pattern_tracking.qt_gui.top_menu_bar.plot.PlotMenu import PlotMenu
from src.pattern_tracking.qt_gui.top_menu_bar.trackers.TrackersMenu import TrackersMenu
from src.pattern_tracking.logic.tracker import TrackerManager
from src.pattern_tracking.qt_gui.widgets.FrameDisplayWidget import FrameDisplayWidget
from src.pattern_tracking.qt_gui.top_menu_bar.video.VideoMenu import VideoMenu
from src.pattern_tracking.shared import constants

class AppMainWindow(QMainWindow):
    """
    Main display to the user. Initializes the application
    with the different menus, sidebar menus and buttons
    """

    def __init__(self, tracker_manager: TrackerManager, live_feed: LiveFeedWrapper, halt_event: threading.Event):
        super().__init__()
        self.halt_event = halt_event
        self.setWindowTitle("Anytrack")
        # -- Attributes
        self._TRACKER_MANAGER = tracker_manager

        # -- Widgets
        self._FRAME_DISPLAY = FrameDisplayWidget(tracker_manager)
        self._PLOTS_CONTAINER_WIDGET = LivePlotterDockWidget(self)

        # -- Menus
        self._VIDEO_MENU = VideoMenu(live_feed)
        self._TRACKERS_MENU = TrackersMenu(tracker_manager, parent=self)
        self._PLOTS_MENU = PlotMenu(tracker_manager, self._PLOTS_CONTAINER_WIDGET)

        # -- Assignments
        self.menuBar().addMenu(self._VIDEO_MENU)
        self.menuBar().addMenu(self._TRACKERS_MENU)
        self.menuBar().addMenu(self._PLOTS_MENU)
        self.addDockWidget(Qt.RightDockWidgetArea, self._PLOTS_CONTAINER_WIDGET)
        self.setCentralWidget(self._FRAME_DISPLAY)

    def get_frame_display_widget(self) -> FrameDisplayWidget:
        """:return: the current frame display widget"""
        return self._FRAME_DISPLAY

    def get_plot_container_widget(self):
        """:return: the current plots container"""
        return self._PLOTS_CONTAINER_WIDGET

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Plus:
            constants.POI_WIDTH  += 1
            constants.POI_HEIGHT += 1
        elif event.key() == Qt.Key_Minus:
            constants.POI_WIDTH  -= 1
            constants.POI_HEIGHT -= 1