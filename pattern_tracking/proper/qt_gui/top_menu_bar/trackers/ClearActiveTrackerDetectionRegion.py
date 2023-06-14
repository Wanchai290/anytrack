from PySide6.QtGui import QAction

from pattern_tracking.proper.logic.tracker.TrackerManager import TrackerManager


class ClearActiveTrackerDetectionRegion(QAction):
    """
    Removes the detection region of the currently active tracker
    """

    def __init__(self, tracker_manager: TrackerManager):
        super().__init__()
        self.setText("Clear detection region")
        self.triggered.connect(tracker_manager.clear_active_tracker_detection_region)
