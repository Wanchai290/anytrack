from typing import Callable

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QWidget

from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.NewTrackerQDialog import NewTrackerQDialog
from pattern_tracking.proper.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager


class CreateTrackerAction(QAction):
    """
    QAction object that generates a dialog window
    for the creation of a tracker.

    Once the tracker is created, it gets added
    to the related tracker manager.

    dev note: this class has a callback attribute to update the GUI that displays
    the currently selected tracker.
    """

    def __init__(self, tracker_manager: TrackerManager,
                 gui_callback: Callable[[AbstractTracker], None],
                 top_level_parent: QWidget = None):
        super().__init__()
        self._TOP_LEVEL_PARENT = top_level_parent
        self._tracker_manager = tracker_manager
        """The manager to which the new tracker will be added to"""
        self._on_creation_complete_callback = gui_callback
        """Will be called once a new tracker has been created"""

        self.setText("New tracker")
        self.triggered.connect(self._new_tracker_dialog)

    def _new_tracker_dialog(self):
        """
        Instantiates a new popup dialog to create a tracker
        If there were no trackers after completion
        """
        set_new_as_default = len(self._tracker_manager.alive_trackers()) == 0

        dlg = NewTrackerQDialog(self._tracker_manager, parent_widget=self._TOP_LEVEL_PARENT)

        if dlg.exec():
            if set_new_as_default:
                self._tracker_manager.set_active_tracker(dlg.get_created_tracker().get_id())
            self._on_creation_complete_callback(dlg.get_created_tracker())


if __name__ == "__main__":
    app = QApplication()
    o = CreateTrackerAction(TrackerManager(), print)
    o._new_tracker_dialog()
