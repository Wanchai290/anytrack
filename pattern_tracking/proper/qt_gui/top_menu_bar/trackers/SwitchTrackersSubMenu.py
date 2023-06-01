import uuid

from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import QMenu, QWidget, QStyle

from pattern_tracking.proper.logic.tracker import AbstractTracker
from pattern_tracking.proper.logic.tracker import TrackerManager


class SwitchTrackersSubMenu(QMenu):
    """
    Independent QMenu object that displays all the trackers
    available, and allows to select which one the user wants
    to edit.
    """

    ACTIVE_TRACKER_ICON = QStyle.StandardPixmap.SP_ArrowRight

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
        :param tracker: The tracker to display in the items
        """
        switch_action = QAction()
        switch_action.setText(tracker.get_name())
        switch_action.setData(tracker.get_id())

        # special way of calling a slot with different args
        self._actions[tracker.get_id()] = switch_action
        switch_action.triggered.connect(lambda: self._update_selected_tracker(tracker))
        self._update_gui_selected_tracker()
        self.addAction(switch_action)

    def _update_selected_tracker(self, tracker: AbstractTracker):
        """
        Changes the active selected tracker in the tracker manager,
        and updates the list of trackers that can be selected
        :param tracker: The new active selected tracker by the user
        """
        # change currently active tracker in manager
        self._TRACKER_MANAGER.set_active_tracker(tracker.get_id())

        # update the GUI accordingly
        self._update_gui_selected_tracker()

    def _update_gui_selected_tracker(self):
        """Highlights the active selected tracker with an arrow icon"""
        # clear icon of all items in this QMenu
        for act in self._actions.values():
            act.setIcon(QPixmap())

        # set right arrow icon for the current tracker's item
        selected_tracker = self._TRACKER_MANAGER.get_active_selected_tracker()
        switch_action = self._actions[selected_tracker.get_id()]
        switch_action.setIcon(
            self.style().standardIcon(SwitchTrackersSubMenu.ACTIVE_TRACKER_ICON)
        )

    def _remove_tracker_item(self, tracker: AbstractTracker):
        """
        Removes the given tracker from the items list
        :param tracker: The tracker to remove from the displayed items
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
