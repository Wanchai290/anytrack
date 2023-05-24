from pattern_tracking.proper.AbstractTracker import AbstractTracker
import numpy as np


class DistanceObserver:
    """
    Given two tracker objects, will compute the Euclidean distance
    between the center of the tracked items of each tracker
    """
    ERR_DIST = -1

    def __init__(self, name: str, t1: AbstractTracker, t2: AbstractTracker):
        self._name = name
        self._t1 = t1
        self._t2 = t2

    def set_tracker1(self, tracker: AbstractTracker):
        self._t1 = tracker

    def set_tracker2(self, tracker: AbstractTracker):
        self._t2 = tracker

    def distance(self) -> float:
        if self._t1 is None or self._t2 is None:
            return DistanceObserver.ERR_DIST

        center_t1 = self._t1.get_found_poi_center()
        center_t2 = self._t2.get_found_poi_center()

        if center_t1 is None or center_t2 is None:
            return DistanceObserver.ERR_DIST

        return np.linalg.norm(center_t1 - center_t2)
