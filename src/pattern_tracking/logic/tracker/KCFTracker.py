from threading import Lock

import cv2 as cv
import numpy as np

from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest
from src.pattern_tracking.shared import utils


class KCFTracker(AbstractTracker):
    """
    Usage of the cv.TrackerKCF object, but with this app's architecture

    dev note: Everytime the POI and/or detection region changes, you need to call
    OpenCV's tracker init() method, and you need to keep track of which image to use when
    the method self.update() is getting called (either the full frame, or the image of the
    detection region). These two checks are done independently, but they are strongly linked !
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
            # use either the full image, or limit to  detection region
            try:
                frame, offset = utils.compute_detection_offset(base_frame, self._template_poi.get_image(), self._detection_region)
            except IndexError:
                return

            # don't do anything if detection bounds is defined, but not valid
            if not self._detection_region.is_undefined() and (self._detection_region.get_xywh()[2:] <= self._template_poi.get_xywh()[2:]).any():
                return

            # compute the location of the POI
            self._init_lock.acquire()
            found, bbox = self._base_tracker.update(frame)
            if found:
                # convert OpenCV bounding box into something usable
                xywh = np.array([int(v) for v in bbox])
                # apply the offset (see utils.compute_detection_offset docs for explanations)
                xywh[:2] += offset
                x, y, w, h = xywh
                # Important note :
                # Since we applied the offset, the given coordinates are now attached to the base frame's plane
                # This is why it becomes the parent image in this RegionOfInterest object
                self._found_poi = RegionOfInterest.new(self._base_frame, x, w, y, h)
                self._draw_poi(self._found_poi)
            self._init_lock.release()

    # -- Overrides
    def set_poi(self, poi: RegionOfInterest):
        super().set_poi(poi)
        self._reset_base_tracker()
        self._initialized = True

    def set_detection_region(self, region: RegionOfInterest):
        # reset the base tracker
        # only possible if a POI is set !
        if not self._template_poi.is_undefined() and not (region.get_xywh()[2:] <= self._template_poi.get_xywh()[2:]).any():
            poi_w, poi_h = self._template_poi.get_xywh()[2:]
            if sum((poi_w, poi_h)) <= sum(region.get_xywh()[2:]):
                self._detection_region = region
                self._reset_base_tracker()

    def _reset_base_tracker(self):
        self._init_lock.acquire()
        self._base_tracker = cv.TrackerKCF_create()

        if self._detection_region.is_undefined():
            self._base_tracker.init(
                self._base_frame,
                self._template_poi.get_xywh()
            )

        else:
            poi_w, poi_h = self._template_poi.get_xywh()[2:]
            poi_offset_x, poi_offset_y = self._template_poi.offset(self._detection_region.get_xywh()[:2], reverse=True)
            self._base_tracker.init(
                self._detection_region.get_image(),
                (poi_offset_x, poi_offset_y, poi_w, poi_h)
            )
        self._init_lock.release()

    def _draw_poi(self, rect: RegionOfInterest | np.ndarray):
        super()._draw_poi(rect)


if __name__ == "__main__":
    a = KCFTracker("")
