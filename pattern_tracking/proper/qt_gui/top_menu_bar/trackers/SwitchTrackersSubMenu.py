import uuid

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget

from pattern_tracking.proper.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager


class SwitchTrackersSubMenu(QMenu):

    def __init__(self, tracker_manager: TrackerManager, parent: QWidget = None):
        super().__init__(parent)
        self._TRACKER_MANAGER = tracker_manager
        self.setTitle("Switch trackers")
        self._actions: dict[uuid.UUID, QAction] = {}
        """Contains the UUID of each tracker and its QAction object"""

    def _add_tracker_item(self, tracker: AbstractTracker):
        """
        Adds a tracker item to this menu, which makes it
        clickable to switch on it
        :param tracker: The tracker to add
        """
        switch_action = QAction(tracker.get_name())
        switch_action.setText(tracker.get_name())
        switch_action.setData(tracker.get_id())

        # special way of calling a slot with different args
        switch_action.triggered.connect(lambda: self._TRACKER_MANAGER.set_active_tracker(tracker.get_id()))
        self._actions[tracker.get_id()] = switch_action
        self.addAction(switch_action)

    def _remove_tracker_item(self, tracker: AbstractTracker):
        """
        Removes the given tracker from the items list
        :param tracker: The tracker to remove
        """
        to_remove = self._actions.pop(tracker.get_id())
        self.removeAction(to_remove)

    def on_tracker_added_callback(self, tracker: AbstractTracker):
        """
        This method should be called everytime a new tracker has been added.
        It will update the GUI to add the new tracker to the list of active
        trackers, so the user can switch to any of the active ones

        dev note: Signals could've been used, but it would have led to the
        same implementation on the high level
        :param tracker: The tracker that has been recently added
        """
        self._add_tracker_item(tracker)
