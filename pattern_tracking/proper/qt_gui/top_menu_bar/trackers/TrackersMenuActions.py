from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QApplication, QDialog

from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.NewTrackerQDialog import NewTrackerQDialog
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager


class TrackersMenuActions:

    def __init__(self, parent_widget: QWidget, tracker_manager: TrackerManager):
        self._PARENT = parent_widget
        self._tracker_manager = tracker_manager
        self._actions: dict[str, QAction] = {}

    def _define_actions(self):
        # create tracker
        create = QAction("New tracker")
        create.triggered.connect(self._new_tracker_dialog)

    def _new_tracker_dialog(self):
        set_new_as_default = len(self._tracker_manager.alive_trackers_names()) == 0

        dlg = NewTrackerQDialog(self._tracker_manager)

        if dlg.exec() and set_new_as_default:
            self._tracker_manager.set_active_tracker(dlg.get_created_tracker().get_name())


if __name__ == "__main__":
    app = QApplication()
    o = TrackersMenuActions(None, TrackerManager())
    o._new_tracker_dialog()
