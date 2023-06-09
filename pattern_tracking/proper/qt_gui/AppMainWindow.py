from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from pattern_tracking.proper.logic.VideoReader import VideoReader
from pattern_tracking.proper.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from pattern_tracking.proper.qt_gui.top_menu_bar.plot.PlotMenu import PlotMenu
from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.TrackersMenu import TrackersMenu
from pattern_tracking.proper.logic.tracker import TrackerManager
from pattern_tracking.proper.qt_gui.FrameDisplayWidget import FrameDisplayWidget
from pattern_tracking.proper.qt_gui.top_menu_bar.video.VideoMenu import VideoMenu


class AppMainWindow(QMainWindow):
    """
    Main display to the user. Initializes the application
    with the different menus, sidebar menus and buttons
    """

    def __init__(self, tracker_manager: TrackerManager, live_feed: VideoReader):
        super().__init__()
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
