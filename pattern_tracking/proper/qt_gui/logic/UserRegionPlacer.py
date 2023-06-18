from __future__ import annotations

import numpy as np

from pattern_tracking.proper.objects.RegionOfInterest import RegionOfInterest
from pattern_tracking.proper.shared.constants import POI_WIDTH, POI_HEIGHT

# used to avoid circular imports because of type hinting
# see https://adamj.eu/tech/2021/05/13/python-type-hints-how-to-fix-circular-imports/
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pattern_tracking.proper.qt_gui.widgets.FrameDisplayWidget import FrameDisplayWidget


class UserRegionPlacer:
    # todo: find a better class name for this
    """
    Handles the creation of a new point of interest
    (or not, depending on if the conditions are met)
    and its assignment to a tracker
    """

    def __init__(self, frame_display_widget: FrameDisplayWidget):
        self._FRAME_DISPLAY_WIDGET = frame_display_widget
        self._drawing = False
        """Defines whether the user is trying to create a new hand-drawn region"""
        self._user_detection_region = RegionOfInterest.new_empty()
        """The current detection region being drawn by the user"""

    def drawing(self) -> bool:
        return self._drawing

    def create_new_poi(self, mx: int, my: int):
        """
        Tries to create a new point of interest in the image.
        Will assign it to the tracker in two cases :
            - The detection region is unspecified
            - The selected POI is inside the detection region
        :param mx: X coordinate of the click of the user
        :param my: Y coordinate of the click of the user
        """
        # TODO: be able to place POI on edges properly
        tracker = self._FRAME_DISPLAY_WIDGET.get_active_selected_tracker()
        # Create the point of interest using the user's selection as
        # the center of the point of interest
        computed_poi = RegionOfInterest.new(
            self._FRAME_DISPLAY_WIDGET.get_current_frame(),
            int(mx - POI_WIDTH / 2), POI_WIDTH, int(my - POI_HEIGHT / 2), POI_HEIGHT
        )

        # Only consider the POI useful if
        #  - the detection region is undefined (thus, we find the POI in the whole frame
        #  - the computed POI is in the detection region
        if tracker.get_detection_region().is_undefined() \
                or tracker.get_detection_region().intersects(computed_poi):
            tracker.set_poi(computed_poi)

    def create_new_detection_region(self, mx: int, my: int):
        """
        Create a new detection region with the user's choice
        Start and end will be the same
        :param mx: X coordinate of the user's mouse when he clicked
        :param my: Y coordinate of the user's mouse when he clicked
        """
        self._drawing = True
        self._user_detection_region = \
            RegionOfInterest.from_points(
                self._FRAME_DISPLAY_WIDGET.get_current_frame(), (mx, my), (mx, my)
            )

    def update_detection_region_end(self, mx_end: int, my_end: int):
        """
        Updates the end point of the detection region for tracking
        :param mx_end: X coordinate of the bottom right point
        :param my_end: Y coordinate of the bottom right point
        """
        self._user_detection_region.set_coords(
            np.array((mx_end, my_end)),
            index=RegionOfInterest.PointCoords.BOTTOM_RIGHT.value,
            normalize=False
        )
        self._FRAME_DISPLAY_WIDGET.get_active_selected_tracker().set_detection_region(self._user_detection_region)

    def end_detection_region_creation(self):
        """
        Disables drawing mode, and assigns the newly made detection region
        to the highlighter
        """
        self._drawing = False
        self._user_detection_region.normalize()
        self._FRAME_DISPLAY_WIDGET.get_active_selected_tracker().set_detection_region(self._user_detection_region)
