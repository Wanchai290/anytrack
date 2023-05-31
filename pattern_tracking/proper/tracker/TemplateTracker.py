import cv2 as cv
import numpy as np

from pattern_tracking.proper.shared import utils, constants
from pattern_tracking.proper.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.objects.RegionOfInterest import RegionOfInterest


class TemplateTracker(AbstractTracker):
    """
    In charge of detecting & tracking a template image in a given
    detection region, or in a whole frame if the detection region is undefined
    """

    def __init__(self, name: str):
        super().__init__(name)

    # -- Methods
    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray):
        # dev note: This isn't the most performant logic structure, there are some checks that are done multiple times
        # but could have been done only once.
        # Doing the latter would have led to less readable code, so I took the first option
        self._base_frame = base_frame
        self._drawing_frame = drawing_frame

        # Update the backing image of the detection region & draw it
        if not self._detection_region.is_undefined():
            self._detection_region.set_parent_image(self._base_frame)
            self._draw_detection_region(self._detection_region.get_coords())

        # Find location of POI if it is defined,
        # and if POI is smaller than region
        if not self._template_poi.is_undefined():
            try:
                self._found_poi = utils.find_template_in_image(
                    self._base_frame,
                    self._template_poi.get_image(),
                    constants.DETECTION_THRESHOLD,
                    detection_bounds=self._detection_region
                )
            except AssertionError:
                self._found_poi = RegionOfInterest.new_empty()

            # Determine what we have to draw
            if self._detection_region.is_undefined():
                if not self._found_poi.is_undefined():
                    self._draw_poi(self._found_poi.get_coords())
            else:
                if self._detection_region.intersects(self._template_poi):
                    self._draw_poi(self._found_poi.get_coords())

    def _draw_poi(self, rect):
        cv.rectangle(
            self._drawing_frame,
            *rect,
            (255, 255, 255),
            2
        )

    def _draw_detection_region(self, rect):
        cv.rectangle(
            self._drawing_frame,
            *rect,
            (0, 255, 0),  # green
            2  # thickness
        )
