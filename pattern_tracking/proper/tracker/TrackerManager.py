from enum import Enum
from typing import Iterable

import numpy as np
from PySide6.QtGui import QAction

from pattern_tracking.proper.interfaces.RemoteQActionsInterface import RemoteQActionsInterface
from pattern_tracking.proper.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.tracker.TemplateTracker import TemplateTracker


class TrackerManager(RemoteQActionsInterface):
    """
    Contains a collection of trackers, and links them
    together so that they all draw their results
    on a single frame to display to the user
    """

    class TrackerType(Enum):
        TEMPLATE_TRACKER = "Template tracker"
        KCF_TRACKER = "KCF Tracker"

    def __init__(self):
        self._active_tracker: AbstractTracker | None = None
        self._collection: dict[str, AbstractTracker] = {}

        self._qt_actions: dict[str, QAction] = {}
        self.init_qt_actions()

    def get_tracker(self, tracker_name: str) -> AbstractTracker | None:
        """
        Get the tracker with the given name
        :param tracker_name: The name of the tracker object to retrieve
        """
        return self._collection[tracker_name]

    def create_tracker(self, name: str, tracker_type: TrackerType) -> AbstractTracker:
        """
        Factory method for creating a new Tracker object
        :param name: The name for the new tracker. Cannot be empty
        :param tracker_type: The type of the tracker, one of TrackerManager.TrackerType
        :return: True if the tracker was successfully created & added to this manager
        """
        if len(name) == 0:
            raise ValueError("The tracker's name cannot be empty !")

        if name in self._collection.keys():
            raise KeyError("All trackers must have different names. \n" +
                           "Please input a different name for the new tracker")

        if tracker_type == TrackerManager.TrackerType.TEMPLATE_TRACKER:
            self._collection[name] = TemplateTracker(name)
        else:
            raise NotImplementedError("This tracker type is not yet implemented !")

        return self._collection[name]

    def add_tracker(self, tracker: AbstractTracker):
        """
        Add a tracker to this manager
        :param tracker: The tracker to add
        """
        self._collection[tracker.get_name()] = tracker

    def remove_tracker(self, tracker_name: str) -> bool:
        """
        Removes the tracker that has the same name as the given one
        :param tracker_name:
        :return: True if the tracker could be removed, false if wasn't here in the first place
                 or if the specified tracker wasn't in this manager's collection
        """
        has_tracker = tracker_name in self._collection.keys()
        if has_tracker:
            self._collection.pop(tracker_name)
        return has_tracker

    def update_trackers(self, live_frame: np.ndarray, drawing_sheet: np.ndarray) -> np.ndarray:
        """
        Updates all trackers with the new live framed passed in parameter,
        so that all trackers compute the new location of the region
        that they're supposed to track
        :param live_frame: The new live video frame to update the trackers
        :param drawing_sheet: The image on which the trackers should draw
        :return: The frame edited by all trackers, that highlights regions tracked
        """
        for tr in self._collection.values():
            tr.update(live_frame, drawing_sheet)
            drawing_sheet = tr.get_edited_frame()

        return drawing_sheet

    def set_active_tracker(self, tracker_name: str):
        tracker = self._collection.get(tracker_name)
        if tracker is None:
            raise ValueError(f"No tracker with the name {tracker_name} is part of this tracker manager")
        self._active_tracker = tracker

    def get_active_selected_tracker(self) -> AbstractTracker | None:
        """
        Gets the current tracker that was selected by the user,
        or None if there are no trackers available
        :return: The current selected tracker or None
        """
        return self._active_tracker

    def alive_trackers_names(self) -> list[str]:
        """Returns the names of all trackers currently in this manager"""
        return list(self._collection.keys())

    # - Overriding methods

    def init_qt_actions(self):
        pass

    def get_qt_actions(self) -> dict[str, QAction]:
        return self._qt_actions

    @staticmethod
    def available_trackers() -> list[TrackerType]:
        return [v[1] for v in enumerate(TrackerManager.TrackerType)]


if __name__ == '__main__':
    print(TrackerManager.available_trackers())
