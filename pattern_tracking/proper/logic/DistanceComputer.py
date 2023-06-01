import uuid

from pattern_tracking.proper.logic.tracker import AbstractTracker
import numpy as np


class DistanceComputer:
    """
    Given two tracker objects, will compute the Euclidean distance
    between the center of the tracked items of each tracker
    """
    ERR_DIST = -1

    def __init__(self, name: str, t1: AbstractTracker, t2: AbstractTracker):
        if len(name.strip()) == 0:
            raise ValueError("The plot name cannot be empty !")
        self._name = name
        self._uuid = uuid.uuid4()
        if t1.get_id() == t2.get_id():
            raise ValueError("The two trackers must be different")
        self._tracker_one = t1
        self._tracker_two = t2

    def get_uuid(self) -> uuid.UUID:
        return self._uuid

    def get_name(self) -> str:
        return self._name

    def get_tracker_one(self) -> AbstractTracker:
        return self._tracker_one

    def get_tracker_two(self) -> AbstractTracker:
        return self._tracker_two

    def set_tracker_one(self, tracker: AbstractTracker):
        self._tracker_one = tracker

    def set_tracker_two(self, tracker: AbstractTracker):
        self._tracker_two = tracker

    def distance(self) -> float:
        if self._tracker_one is None or self._tracker_two is None:
            return DistanceComputer.ERR_DIST

        center_t1 = self._tracker_one.get_found_poi_center()
        center_t2 = self._tracker_two.get_found_poi_center()

        if center_t1 is None or center_t2 is None:
            return DistanceComputer.ERR_DIST

        return np.linalg.norm(center_t1 - center_t2)

    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return self._uuid == other.get_uuid()
