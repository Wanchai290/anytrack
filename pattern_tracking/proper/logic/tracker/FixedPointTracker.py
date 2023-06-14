from pattern_tracking.proper.logic.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.objects.RegionOfInterest import RegionOfInterest

import numpy as np
import cv2 as cv


class FixedPointTracker(AbstractTracker):
    """
    This tracker doesn't really track anything, it just sets itself somewhere and doesn't move
    """

    def __init__(self, name: str):
        super().__init__(name)

    def set_detection_region(self, region: RegionOfInterest):
        # because a fixed point doesn't need specific bounds
        return

    # -- Overrides
    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray):
        super().update(base_frame, drawing_frame)
        if not self._template_poi.is_undefined():
            self._draw_poi(self._template_poi)

    def set_poi(self, poi: RegionOfInterest):
        super().set_poi(poi)
        self._found_poi = poi
