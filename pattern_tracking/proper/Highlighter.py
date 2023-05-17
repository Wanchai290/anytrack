import cv2 as cv
import numpy as np

from pattern_tracking.proper import utils, constants
from pattern_tracking.proper.RegionOfInterest import RegionOfInterest


class Highlighter:

    def __init__(self):
        self.__detection_region = RegionOfInterest.new_empty()
        """The region in which we limit ourselves to find the POI"""
        self.__poi = RegionOfInterest.new_empty()
        """The part of the image that we want to find in the current frame"""
        self.__frame: cv.Mat | np.ndarray = np.zeros((1, 1))
        """The current frame to be displayed to the user, with the highlighted zones"""

    # -- Getters

    def get_edited_frame(self) -> cv.Mat | np.ndarray:
        return self.__frame

    def get_detection_region(self) -> RegionOfInterest:
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

        if not self.__detection_region.is_undefined():
            self.__detection_region.set_parent_image(self.__frame)
            self.__draw_detection_region(self.__detection_region.get_coords())

        if not self.__poi.is_undefined():
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

        # # Just display the frame if there is nothing to track
        # if self.__detection_region.is_undefined() \
        #         and self.__poi.is_undefined():
        #     return
        #
        # # change whether we find the POI in a region, or in the whole frame
        # if self.__detection_region.is_undefined():
        #     region = self.__frame
        #     offset: np.ndarray = np.array([0, 0])
        # else:
        #     region = self.__detection_region.get_image()
        #     offset: np.ndarray = self.__detection_region.get_coords(
        #         RegionOfInterest.PointCoords.TOP_LEFT.value
        #     )
        #     # Draw the detection region as well
        #     self.__draw_detection_region(self.__detection_region)
        #
        # # Compute location of POI
        # if not self.__poi.is_undefined():
        #     found_poi = utils.find_template_in_image(
        #         region,
        #         self.__poi.get_image(),
        #         constants.DETECTION_THRESHOLD
        #     )
        #     # Draw computed POI location on display frame, only if the POI has been found
        #     # TODO: split these two conditions, avoid useless computing power usage
        #     if not found_poi.is_undefined():
        #         # Display POI only in two cases :
        #         # - if detection region is valid and POI is in detection region
        #         # - if detection region is not specified
        #         if (not self.__detection_region.is_undefined() and self.__detection_region.intersects(self.__poi)) \
        #                 or self.__detection_region.is_undefined():
        #             found_poi = found_poi.offset(offset)
        #             self.__draw_poi(found_poi)

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
