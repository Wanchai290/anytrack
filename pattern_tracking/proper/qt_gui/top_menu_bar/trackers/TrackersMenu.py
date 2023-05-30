from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from pattern_tracking.proper.tracker.TrackerManager import TrackerManager


class TrackersMenu(QMenu):

    def __init__(self, tracker_manager: TrackerManager):
        super().__init__()
        self._TRACKER_MANAGER = tracker_manager

        self._initialize_items()

    def _initialize_items(self):
        # self.addAction(QAction())
        pass
