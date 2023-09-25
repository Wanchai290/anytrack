from PySide6.QtWidgets import QMenu, QWidget

from src.pattern_tracking.qt_gui.top_menu_bar.trackers.ClearActiveTrackerDetectionRegion import \
    ClearActiveTrackerDetectionRegion
from src.pattern_tracking.qt_gui.top_menu_bar.trackers.CreateTrackerAction import CreateTrackerAction
from src.pattern_tracking.qt_gui.top_menu_bar.trackers.SwitchTrackersSubMenu import SwitchTrackersSubMenu
from src.pattern_tracking.logic.tracker import TrackerManager


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

        self._CLEAR_ACTIVE_TRACKER_DETREG = ClearActiveTrackerDetectionRegion(tracker_manager)

        # menu parameters
        self.setTitle(TrackersMenu.DEFAULT_NAME if name is None else name)
        self.addAction(self._CREATE_TRACKER_ACTION)
        self.addAction(self._CLEAR_ACTIVE_TRACKER_DETREG)
        self.addMenu(self._SWITCH_TRACKERS_SUBMENU)
