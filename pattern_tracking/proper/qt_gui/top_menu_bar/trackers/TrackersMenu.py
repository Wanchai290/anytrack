from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.CreateTrackerAction import CreateTrackerAction
from pattern_tracking.proper.qt_gui.top_menu_bar.trackers.SwitchTrackersSubMenu import SwitchTrackersSubMenu
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager


class TrackersMenu(QMenu):
    """
    Independent menu that is meant to be placed added to a MenuBar parent object.
    Displays all actions possible with the trackers of the app
    """

    DEFAULT_NAME = "Trackers"
    """Default text displayed that represents this menu's clickable in the GUI"""

    def __init__(self, tracker_manager: TrackerManager, name: str = None):
        super().__init__()
        self._TRACKER_MANAGER = tracker_manager

        self._SWITCH_TRACKERS_SUBMENU = SwitchTrackersSubMenu(tracker_manager)
        """Sub-menu containing the buttons to switch to any tracker"""

        self._CREATE_TRACKER_ACTION = \
            CreateTrackerAction(
                self._TRACKER_MANAGER,
                self._SWITCH_TRACKERS_SUBMENU.on_tracker_added_callback
            )
        """Button that opens a popup dialog to create a new tracker"""

        # menu parameters
        self.setTitle(TrackersMenu.DEFAULT_NAME if name is None else name)
        self._initialize_items()

    def _initialize_items(self):
        """Instantiates all the items of this menu"""
        self.addAction(self._CREATE_TRACKER_ACTION)
        self.addMenu(self._SWITCH_TRACKERS_SUBMENU)
