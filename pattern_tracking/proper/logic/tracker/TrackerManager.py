import uuid
from threading import Lock

import numpy as np
from PySide6.QtGui import QAction

from pattern_tracking.proper.logic.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.logic.tracker.KCFTracker import KCFTracker
from pattern_tracking.proper.logic.tracker.TemplateTracker import TemplateTracker


class TrackerManager:
    """
    Contains a collection of trackers, and links them
    together so that they all draw their results
    on a single frame to display to the user
    """

    def __init__(self):
        self._active_tracker: AbstractTracker | None = None
        """The tracker that the user is currently editing"""
        self._collection: dict[uuid.UUID, AbstractTracker] = {}
        """Collection of trackers of this manager"""
        self._collection_mutex = Lock()
        """
        Any modification operation MUST get the lock before modifying the collection of this manager
        Otherwise, the program might run into a RuntimeError because the collection would change while it's being read
        """

        self._qt_actions: dict[str, QAction] = {}

    def get_tracker(self, tracker_id: uuid.UUID) -> AbstractTracker | None:
        """
        Get the tracker with the given UUID
        :param tracker_id: The UUID of the tracker object to retrieve
        """
        return self._collection[tracker_id]

    def create_tracker(self, name: str, tracker_type: AbstractTracker.TrackerType) -> AbstractTracker:
        """
        Factory method for creating a new Tracker object
        :param name: The name for the new tracker. Cannot be empty
        :param tracker_type: The type of the tracker, one of AbstractTracker.TrackerType
        :return: True if the tracker was successfully created & added to this manager
        """
        if len(name) == 0:
            raise ValueError("The tracker's name cannot be empty !")

        name = name.strip()

        if name in [t.get_name() for t in self._collection.values()]:
            raise KeyError("All trackers must have different names." +
                           "Please input a different name for the new tracker")

        self._collection_mutex.acquire(blocking=True)
        if tracker_type == AbstractTracker.TrackerType.TEMPLATE_TRACKER:
            tracker = TemplateTracker(name)
            self._collection[tracker.get_id()] = tracker
        elif tracker_type == AbstractTracker.TrackerType.KCF_TRACKER:
            tracker = KCFTracker(name)
            self._collection[tracker.get_id()] = tracker
        else:
            self._collection_mutex.release()
            raise NotImplementedError("This tracker type is not yet implemented !")

        # release lock anyway
        self._collection_mutex.release()

        return self._collection[tracker.get_id()]

    def add_tracker(self, tracker: AbstractTracker):
        """
        Add a tracker to this manager
        :param tracker: The tracker to add
        """
        self._collection[tracker.get_id()] = tracker

    def remove_tracker(self, tracker_id: uuid.UUID) -> bool:
        """
        Removes the tracker that has the same name as the given one
        :param tracker_id: The UUID of the tracker
        :return: True if the tracker could be removed, false if wasn't here in the first place
                 or if the specified tracker wasn't in this manager's collection
        """
        has_tracker = tracker_id in self._collection.keys()
        if has_tracker:
            self._collection_mutex.acquire(blocking=True)
            self._collection.pop(tracker_id)
            self._collection_mutex.release()
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
        # Wait for any modification operation to end
        self._collection_mutex.acquire(blocking=True)
        for tr in self._collection.values():
            tr.update(live_frame, drawing_sheet)
            drawing_sheet = tr.get_edited_frame()

        self._collection_mutex.release()
        return drawing_sheet

    def set_active_tracker(self, tracker_id: uuid.UUID):
        tracker = self._collection.get(tracker_id)
        if tracker is None:
            raise ValueError(f"No tracker with the UUID \"{tracker_id}\" is part of this tracker manager")
        self._active_tracker = tracker

    def get_active_selected_tracker(self) -> AbstractTracker | None:
        """
        Gets the current tracker that was selected by the user,
        or None if there are no trackers available
        :return: The current selected tracker or None
        """
        if self._active_tracker is None:
            raise ValueError("No active tracker set !")
        return self._active_tracker

    def alive_trackers(self) -> dict[uuid.UUID, AbstractTracker]:
        """Returns the UUIDs and names of all trackers currently in this manager"""
        return {identifier: tracker for (identifier, tracker) in self._collection.items()}

    @staticmethod
    def available_tracker_types() -> list[AbstractTracker.TrackerType]:
        return [v[1] for v in enumerate(AbstractTracker.TrackerType)]


if __name__ == '__main__':
    print(TrackerManager.available_tracker_types())
