from threading import Lock

import cv2 as cv
import numpy as np

from pattern_tracking.proper.logic.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.objects.RegionOfInterest import RegionOfInterest


class KCFTracker(AbstractTracker):
    """
    Usage of the cv.TrackerKCF object, but with this app's architecture

    dev note: Everytime the POI and/or detection region changes, you need to call
    OpenCV's tracker init() method, and you need to keep track of which image to use when
    the method self.update() is getting called (either the full frame, or the image of the
    detection region)
    """
    def __init__(self, name: str):
        super().__init__(name)
        self._base_tracker = cv.TrackerKCF_create()
        """The base object from the OpenCV API"""
        self._init_lock = Lock()
        """Lock used to not update the tracker while it is being renewed (reinitialized)"""

    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray):
        super().update(base_frame, drawing_frame)
        if self._initialized:
            # use either the full image, or limit to detection region
            frame = base_frame if self._detection_region.is_undefined() else self._detection_region.get_image()

            # compute the location of the POI
            self._init_lock.acquire()
            found, bbox = self._base_tracker.update(frame)
            if found:
                (x, y, w, h) = [int(v) for v in bbox]
                self._draw_poi(RegionOfInterest.new(frame, x, w, y, h))
            self._init_lock.release()

    def _draw_poi(self, rect):
        cv.rectangle(
            self._drawing_frame,
            *rect,
            (255, 255, 255),
            2
        )

    # TODO: currently a copy/paste from TemplateTracker, but lets itself be customizable
    def _draw_detection_region(self, rect):
        cv.rectangle(
            self._drawing_frame,
            *rect,
            (0, 255, 0),  # green
            2  # thickness
        )

    # -- Overrides
    def set_poi(self, poi: RegionOfInterest):
        super().set_poi(poi)
        being_reset = False
        if self._initialized:
            self._init_lock.acquire(blocking=True)
            self._base_tracker = cv.TrackerKCF_create()
            being_reset = True

        self._base_tracker.init(
            poi.get_parent_image(),
            poi.get_xywh()
        )

        if being_reset:
            self._init_lock.release()

        self._initialized = True

    def set_detection_region(self, region: RegionOfInterest):
        super().set_detection_region(region)
        # reset the base tracker
        # TODO/


if __name__ == "__main__":
    a = KCFTracker("")
