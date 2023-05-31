from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.CreateTrackerAction import CreateTrackerAction
from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.SwitchTrackersSubMenu import SwitchTrackersSubMenu
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager


class TrackersMenu(QMenu):

    DEFAULT_NAME = "Trackers"

    def __init__(self, tracker_manager: TrackerManager, name: str = None):
        super().__init__()
        self._TRACKER_MANAGER = tracker_manager

        self._SWITCH_TRACKERS_SUBMENU = SwitchTrackersSubMenu(tracker_manager)

        self._CREATE_TRACKER_ACTION = \
            CreateTrackerAction(
                self._TRACKER_MANAGER,
                self._SWITCH_TRACKERS_SUBMENU.on_tracker_added_callback
            )

        self.setTitle(TrackersMenu.DEFAULT_NAME if name is None else name)
        self._initialize_items()

    def _initialize_items(self):
        self.addAction(self._CREATE_TRACKER_ACTION)
        self.addMenu(self._SWITCH_TRACKERS_SUBMENU)
