from abc import abstractmethod

import cv2 as cv
import numpy as np

from pattern_tracking.proper import utils, constants
from pattern_tracking.proper.AbstractTracker import AbstractTracker
from pattern_tracking.proper.RegionOfInterest import RegionOfInterest


class TemplateTracker(AbstractTracker):
    """
    In charge of detecting & tracking a template image in a given
    detection region, or in a whole frame if the detection region is undefined
    """

    def __init__(self, name: str):
        super().__init__(name)

    # -- Getters

    # -- Methods
    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray):
        """
        Updates the tracking of the current POI in the given
        detection region
        :param base_frame: The current new frame that came from a video feed
        :param drawing_frame: The frame on which the highlighter will draw on
        """
        self._base_frame = base_frame
        self._drawing_frame = drawing_frame

        # Update the backing image of the detection region & draw it
        if not self._detection_region.is_undefined():
            self._detection_region.set_parent_image(self._base_frame)
            self._draw_detection_region(self._detection_region.get_coords())

        # Find location of POI if it is defined,
        # and if POI is smaller than region
        if not self._poi.is_undefined() \
                and (np.array(self._poi.get_image().shape) <= np.array(self._detection_region.get_image().shape)).all():
            found_poi = utils.find_template_in_image(
                self._base_frame,
                self._poi.get_image(),
                constants.DETECTION_THRESHOLD,
                detection_bounds=self._detection_region
            )

            if self._detection_region.is_undefined():
                if not found_poi.is_undefined():
                    self._draw_poi(found_poi.get_coords())
            else:
                if self._detection_region.intersects(self._poi):
                    self._draw_poi(found_poi.get_coords())

    def _draw_poi(self, rect: np.ndarray):
        """
        Draws a rectangle highlighting the point of interest
        on the frame of this object.
        :param rect: The rectangle to draw on the object's frame
        """
        cv.rectangle(
            self._drawing_frame,
            *rect,
            (255, 255, 255),
            2
        )

    def _draw_detection_region(self, rect: RegionOfInterest):
        """
        Draw the region in which to find the POI
        on the frame of this object.
        :param rect: The rectangle to draw on the object's frame
        """
        cv.rectangle(
            self._drawing_frame,
            *rect,
            (0, 255, 0),  # green
            2  # thickness
        )
