import numpy as np

from pattern_tracking.proper.AbstractTracker import AbstractTracker


class TrackerManager:
    """
    Contains a collection of trackers, and links them
    together so that they all draw their results
    on a single frame to display to the user
    """

    def __init__(self):
        self._active_tracker: AbstractTracker | None = None
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
