import cv2 as cv
import numpy as np

from pattern_tracking.proper import utils, constants
from pattern_tracking.proper.RegionOfInterest import RegionOfInterest


class Highlighter:
    """
    In charge of detecting & tracking a template image in a given
    detection region, or in a whole frame if the detection region is undefined
    """

    def __init__(self):
        self.__detection_region = RegionOfInterest.new_empty()
        """The region in which we limit ourselves to find the POI"""
        self.__poi = RegionOfInterest.new_empty()
        """The part of the image that we want to find in the current frame"""
        self.__frame: cv.Mat | np.ndarray = np.zeros((1, 1))
        """The current frame to be displayed to the user, with the highlighted zones"""

    # -- Getters

    def get_edited_frame(self) -> cv.Mat | np.ndarray:
        """:return: The frame that has been edited by this highlighter"""
        return self.__frame

    def get_detection_region(self) -> RegionOfInterest:
        """:return: The detection region of this object"""
        return self.__detection_region

    def set_detection_region(self, region: RegionOfInterest):
        self.__detection_region = region

    def set_poi(self, poi: RegionOfInterest):
        self.__poi = poi

    # -- Methods
    def update(self, frame: cv.Mat | np.ndarray):
        """
        Updates the tracking of the current POI in the given
        detection region
        :param frame: The current new frame that came from a video feed
        """
        self.__frame = frame

        # Update the backing image of the detection region & draw it
        if not self.__detection_region.is_undefined():
            self.__detection_region.set_parent_image(self.__frame)
            self.__draw_detection_region(self.__detection_region.get_coords())

        # Find location of POI if it is defined,
        # and if POI is smaller than region
        if not self.__poi.is_undefined() \
                and (np.array(self.__poi.get_image().shape) <= np.array(self.__detection_region.get_image().shape)).all():
            found_poi = utils.find_template_in_image(
                self.__frame,
                self.__poi.get_image(),
                constants.DETECTION_THRESHOLD,
                detection_bounds=self.__detection_region
            )

            if self.__detection_region.is_undefined():
                if not found_poi.is_undefined():
                    self.__draw_poi(found_poi.get_coords())
            else:
                if self.__detection_region.intersects(self.__poi):
                    self.__draw_poi(found_poi.get_coords())

    def __draw_poi(self, rect: np.ndarray):
        """
        Draws a rectangle highlighting the point of interest
        on the frame of this object.
        :param rect: The rectangle to draw on the object's frame
        """
        cv.rectangle(
            self.__frame,
            *rect,
            (255, 255, 255),
            2
        )

    def __draw_detection_region(self, rect: RegionOfInterest):
        """
        Draw the region in which to find the POI
        on the frame of this object.
        :param rect: The rectangle to draw on the object's frame
        """
        cv.rectangle(
            self.__frame,
            *rect,
            (0, 255, 0),  # green
            2  # thickness
        )
