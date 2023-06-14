import uuid
from abc import ABC, abstractmethod

import cv2 as cv
import numpy as np

from pattern_tracking.proper.shared import utils
from pattern_tracking.proper.objects.RegionOfInterest import RegionOfInterest


class AbstractTracker(ABC):
    """
    This class is used as a base for all trackers implemented in the software.
    To create a new tracker, you must extend this base, and implement the
    update() method. You also need to define a new TrackerType enum value below, and
    modify the TrackerManager class to allow the creation of your new tracker in the GUI
    """
    DEFAULT_POI_COLOR = (255, 255, 255)
    DEFAULT_BOUNDS_COLOR = (0, 255, 0)

    def __init__(self, name: str,
                 poi_rgb: tuple[int, int, int] = DEFAULT_POI_COLOR,
                 detection_bounds_rgb: tuple[int, int, int] = DEFAULT_BOUNDS_COLOR):
        self._id = uuid.uuid4()
        """Unique identifier"""
        self._name = name
        """Name of the tracker. Recommended to be unique among all trackers"""
        self._detection_region = RegionOfInterest.new_empty()
        """The region in which we limit ourselves to find the POI"""
        self._template_poi = RegionOfInterest.new_empty()
        """The part of the image that we want to find in the current frame"""
        self._found_poi = RegionOfInterest.new_empty()
        """The region in which the POI has been found in the given base frame
           Must be updated by the child class !
        """
        self._base_frame: cv.Mat | np.ndarray = np.zeros((1, 1))
        """The current frame to be displayed to the user, with the highlighted zones"""
        self._drawing_frame = np.zeros(self._base_frame.shape)
        """A copy of the base frame, that will be edited by the highlighter"""
        self._initialized = False
        """Whether this tracker has been initialized once
           Only used by OpenCV's trackers, to avoid computing detection
           if the tracker wasn't properly initialized"""

        self._poi_color = poi_rgb
        """Color used to highlight the POI"""
        self._detection_region_color = detection_bounds_rgb
        """Color used to highlight the detection region"""

    def get_edited_frame(self) -> cv.Mat | np.ndarray:
        """:return: The frame that has been edited by this highlighter"""
        return self._drawing_frame

    def get_id(self) -> uuid.UUID:
        """:return The unique identifier of this tracker"""
        return self._id

    def get_name(self) -> str:
        """:return: The name of this tracker"""
        return self._name

    def get_detection_region(self) -> RegionOfInterest:
        """:return: The detection region of this object"""
        return self._detection_region

    def set_detection_region(self, region: RegionOfInterest):
        self._detection_region = region

    def set_poi(self, poi: RegionOfInterest):
        self._template_poi = poi

    def get_found_poi_center(self) -> np.ndarray | None:
        """:return: Coordinates of the center of the location of the POI in this tracker's frame"""
        # TODO: add tests
        if self._found_poi.is_undefined():
            return None

        return utils.middle_of(*self._found_poi.get_coords())

    @abstractmethod
    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray):
        """
        This method is the core of any tracker. It must locate the POI to find in the given image,
        by limiting the search to a specific detection region (if it is defined).

        If the POI has been found, you must update the self._found_poi attribute.

        It should draw the result onto the drawing_frame parameter, that must be of the
        same shape as the given image.
        :param base_frame: The given image in which to find the POI
        :param drawing_frame: The image to highlight the POI's location on
        """
        self._base_frame = base_frame
        self._drawing_frame = drawing_frame

        # Update the backing image of the detection region & draw it
        if not self._detection_region.is_undefined():
            self._detection_region.set_parent_image(self._base_frame)
            self._draw_detection_region(self._detection_region.get_coords())

    def _draw_poi(self, rect: RegionOfInterest | np.ndarray):
        """
        Draws a rectangle highlighting the point of interest
        on the frame of this object.
        :param rect: The rectangle to draw on the object's frame
        """
        cv.rectangle(
            self._drawing_frame,
            *rect,
            self._poi_color,
            2
        )

    def _draw_detection_region(self, rect: RegionOfInterest | np.ndarray):
        """
        Draw the region in which to find the POI
        on the frame of this object.
        :param rect: The rectangle to draw on the object's frame
        """
        cv.rectangle(
            self._drawing_frame,
            *rect,
            self._detection_region_color,
            2
        )
