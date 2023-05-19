from threading import Event

import cv2 as cv
import numpy as np

from constants import POI_WIDTH, POI_HEIGHT
from pattern_tracking.proper.AbstractTracker import AbstractTracker
from pattern_tracking.proper.RegionOfInterest import RegionOfInterest


class GUI:
    """
    User interface class
    Handles mouse interactions and some logic when redefining
    the region of interest and point of interest to track
    """

    def __init__(self, window_name: str,
                 video_feed_shape: tuple[int, int],
                 highlighter: AbstractTracker,
                 halt_event: Event):

        self._WIN_NAME = window_name
        """The name of the window displayed"""
        self._key_pressed = ord(" ")
        """The last key pressed by the user"""
        self._drawing = False
        """Defines whether the user is drawing something onto the window"""

        self._current_frame = np.zeros(video_feed_shape)
        """The currently displayed image to the user"""

        self._HIGHLIGHTER = highlighter
        """The unique highlighter object"""
        self._halt = halt_event
        """Event used to stop all actions of the program"""

    def start_gui(self):
        # WINDOW_GUI_NORMAL to disable default right-click dropdown menus
        cv.namedWindow(self._WIN_NAME, cv.WINDOW_GUI_NORMAL)

        # enable OpenGL
        cv.setWindowProperty(self._WIN_NAME, cv.WND_PROP_OPENGL, 1)

        cv.setMouseCallback(self._WIN_NAME, self._mouse_click_handler, self._HIGHLIGHTER)

    def change_frame_to_display(self, frame: np.ndarray):
        self._current_frame = frame
        cv.imshow(self._WIN_NAME, frame)
        self._key_pressed = cv.waitKey(1)
        if self._key_pressed == ord('q'):
            self._halt.set()

    def _mouse_click_handler(self, event, x, y, flags, param: AbstractTracker):

        highlighter = param
        current_frame = self._current_frame

        if event == cv.EVENT_LBUTTONDOWN:
            self._place_poi(current_frame, highlighter, x, y)

        elif event == cv.EVENT_RBUTTONDOWN:
            self._create_new_detection_region(x, y)

        elif event == cv.EVENT_MOUSEMOVE and self._drawing:
            self._update_detection_region_end(x, y)
            highlighter.set_detection_region(self.__detection_region)

        elif event == cv.EVENT_RBUTTONUP:
            self._end_detection_region_creation()
            highlighter.set_detection_region(self.__detection_region)

    def _place_poi(self, current_frame: np.ndarray, highlighter: AbstractTracker, x: int, y: int):
        """
        Tries to create a new point of interest in the image.
        Will assign it to the highlighter in two cases :
            - The detection region is unspecified
            - The selected POI is inside the detection region
        :param current_frame: The current frame grabbed from the live feed
        :param highlighter: The highlighter objects
        :param x: X coordinate of the click of the user
        :param y: Y coordinate of the click of the user
        """
        # TODO: be able to place POI on edges properly

        # Create the point of interest using the user's selection as
        # the center of the point of interest
        computed_poi = RegionOfInterest.new(
            current_frame,
            int(x - POI_WIDTH / 2), POI_WIDTH, int(y - POI_HEIGHT / 2), POI_HEIGHT
        )

        # Only consider the POI useful if
        #  - the detection region is undefined (thus, we find the POI in the whole frame
        #  - the computed POI is in the detection region
        if highlighter.get_detection_region().is_undefined() \
                or highlighter.get_detection_region().intersects(computed_poi):
            # TODO: handle adding another point
            highlighter.set_poi(computed_poi)

    def _create_new_detection_region(self, x: int, y: int):
        """
        Create a new detection region with the user's choice
        Start and end will be the same
        :param x: X coordinate of the user's mouse when he clicked
        :param y: Y coordinate of the user's mouse when he clicked
        """
        self._drawing = True
        self.__detection_region = \
            RegionOfInterest.from_points(self._current_frame, (x, y), (x, y))

    def _update_detection_region_end(self, x_end: int, y_end: int):
        """
        Updates the end point of the detection region for tracking
        :param x_end: X coordinate of the bottom right point
        :param y_end: Y coordinate of the bottom right point
        """
        self.__detection_region.set_coords(
            np.array((x_end, y_end)),
            index=RegionOfInterest.PointCoords.BOTTOM_RIGHT.value,
            normalize=False
        )

    def _end_detection_region_creation(self):
        """
        Disables drawing mode, and assigns the newly made detection region
        to the highlighter
        """
        self._drawing = False
        self.__detection_region.normalize()
