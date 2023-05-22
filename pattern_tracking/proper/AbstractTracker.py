from abc import ABC, abstractmethod

import cv2 as cv
import numpy as np

from pattern_tracking.proper.RegionOfInterest import RegionOfInterest


class AbstractTracker(ABC):

    def __init__(self, name: str):
        self._name = name
        """Name of the tracker. Cannot (and shouldn't) be modified"""
        self._detection_region = RegionOfInterest.new_empty()
        """The region in which we limit ourselves to find the POI"""
        self._template_poi = RegionOfInterest.new_empty()
        """The part of the image that we want to find in the current frame"""
        self._found_poi = RegionOfInterest.new_empty()
        """The region in which the POI has been found in the given base frame"""
        self._base_frame: cv.Mat | np.ndarray = np.zeros((1, 1))
        """The current frame to be displayed to the user, with the highlighted zones"""
        self._drawing_frame = np.zeros(self._base_frame.shape)
        """A copy of the base frame, that will be edited by the highlighter"""

    def get_edited_frame(self) -> cv.Mat | np.ndarray:
        """:return: The frame that has been edited by this highlighter"""
        return self._drawing_frame

    def get_name(self) -> str:
        return self._name

    def get_detection_region(self) -> RegionOfInterest:
        """:return: The detection region of this object"""
        return self._detection_region

    def set_detection_region(self, region: RegionOfInterest):
        self._detection_region = region

    def set_poi(self, poi: RegionOfInterest):
        self._template_poi = poi

    @abstractmethod
    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray):
        pass

    @abstractmethod
    def _draw_poi(self, rect: np.ndarray):
        pass

    @abstractmethod
    def _draw_detection_region(self, rect: RegionOfInterest):
        pass
