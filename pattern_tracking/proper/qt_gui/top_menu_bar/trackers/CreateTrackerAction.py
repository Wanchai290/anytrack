from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication

from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.NewTrackerQDialog import NewTrackerQDialog
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager


class CreateTrackerAction(QAction):

    def __init__(self, tracker_manager: TrackerManager):
        super().__init__()
        self.setText("New tracker")
        self._tracker_manager = tracker_manager
        self.triggered.connect(self._new_tracker_dialog)

    def _new_tracker_dialog(self):
        set_new_as_default = len(self._tracker_manager.alive_trackers_names()) == 0

        dlg = NewTrackerQDialog(self._tracker_manager)

        if dlg.exec() and set_new_as_default:
            self._tracker_manager.set_active_tracker(dlg.get_created_tracker().get_name())


if __name__ == "__main__":
    app = QApplication()
    o = CreateTrackerAction(TrackerManager())
    o._new_tracker_dialog()
