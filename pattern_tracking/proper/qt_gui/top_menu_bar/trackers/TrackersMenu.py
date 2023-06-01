from PySide6.QtWidgets import QMenu, QWidget

from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.CreateTrackerAction import CreateTrackerAction
from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.SwitchTrackersSubMenu import SwitchTrackersSubMenu
from pattern_tracking.proper.logic.tracker import TrackerManager


class TrackersMenu(QMenu):
    """
    Independent menu that is meant to be placed added to a MenuBar parent object.
    Displays all actions possible with the trackers of the app
    """

    DEFAULT_NAME = "Trackers"
    """Default text displayed that represents this menu's clickable in the GUI"""

    def __init__(self, tracker_manager: TrackerManager, name: str = None, parent: QWidget = None):
        super().__init__(parent)
        self._TRACKER_MANAGER = tracker_manager

        self._SWITCH_TRACKERS_SUBMENU = SwitchTrackersSubMenu(tracker_manager)
        """Sub-menu containing the buttons to switch to any tracker"""

        self._CREATE_TRACKER_ACTION = \
            CreateTrackerAction(
                self._TRACKER_MANAGER,
                self._SWITCH_TRACKERS_SUBMENU.on_tracker_added_callback,
                top_level_parent=self.parent()
            )
        """Button that opens a popup dialog to create a new tracker"""

        # menu parameters
        self.setTitle(TrackersMenu.DEFAULT_NAME if name is None else name)
        self.addAction(self._CREATE_TRACKER_ACTION)
        self.addMenu(self._SWITCH_TRACKERS_SUBMENU)
