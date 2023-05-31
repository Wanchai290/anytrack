from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.CreateTrackerAction import CreateTrackerAction
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager


class TrackersMenu(QMenu):

    DEFAULT_NAME = "Trackers"

    def __init__(self, tracker_manager: TrackerManager, name: str = None):
        super().__init__()
        self._TRACKER_MANAGER = tracker_manager
        self._actions = [
            CreateTrackerAction(self._TRACKER_MANAGER)
        ]
        self.setTitle(TrackersMenu.DEFAULT_NAME if name is None else name)
        self._initialize_items()

    def _initialize_items(self):
        # self.addAction(QAction())
        self.addActions(self._actions)
