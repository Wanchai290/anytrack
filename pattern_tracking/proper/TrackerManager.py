from typing import Set

from pattern_tracking.proper.AbstractTracker import AbstractTracker


class TrackerManager:
    """
    Contains a collection of trackers, and links them
    together so that they all draw their results
    on a single frame to display to the user
    """

    def __init__(self):
        self._collection: dict[str, AbstractTracker] = {}

    def get_tracker(self, tracker_name: str) -> AbstractTracker | None:
        """
        Get the tracker with the given name
        :param tracker_name: The name of the tracker object to retrieve
        """
        return self._collection[tracker_name]

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
