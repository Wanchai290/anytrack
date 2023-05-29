import PySide6.QtCore
from PySide6.QtGui import QMouseEvent, QPixmap, QImage
from PySide6.QtWidgets import QLabel

import numpy as np

from pattern_tracking.proper.TrackerManager import TrackerManager
from pattern_tracking.proper.qt_gui.UserRegionPlacer import UserRegionPlacer


class FrameDisplayWidget(QLabel):
    """
    QT widget displaying the most recent available frame,
    on which is highlighted the current region of interests
    being tracked.

    The logic to know whether to call the bindings or not is performed in this object
    Updates to the region of interest or trackers is done in the UserRegionPlacer object
    """

    def __init__(self, tracker_manager: TrackerManager):
        super().__init__()

        self._USER_REGION_PLACER = UserRegionPlacer(self)
        """
        Logic object for user mouse interaction
        The methods of the mouse events on this widget
        are bound to methods of this object 
        """
        self._current_frame: np.ndarray | None = None
        """The currently displayed image to the user"""
        self._tracker_manager = tracker_manager
        """Contains all the trackers, and the current active one"""

        self._frame_pixmap = QPixmap("cat-sample_1313.jpg")
        self.setPixmap(self._frame_pixmap)

    def get_current_frame(self):
        return self._current_frame

    def change_frame_to_display(self, frame: np.ndarray):
        """
        Updates the current image displayed by this QLabel,
        by converting the passed NumPy frame as a QPixmap
        Everything is taken from https://stackoverflow.com/a/35857856
        Why do it again if someone did it already ?

        :param frame: The frame to be displayed
        """
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.setPixmap(QPixmap(q_img))

    # -- Mouse events binding
    # We override Qt's mouse interaction methods to do our stuff

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == PySide6.QtCore.Qt.MouseButton.LeftButton:
            self._USER_REGION_PLACER.create_new_poi(
                self._tracker_manager.get_active_selected_tracker(),
                event.x(),
                event.y()
            )
        elif event.button() == PySide6.QtCore.Qt.MouseButton.RightButton:
            self._USER_REGION_PLACER.create_new_detection_region(event.x(), event.y())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._USER_REGION_PLACER.drawing():
            self._USER_REGION_PLACER.update_detection_region_end(event.x(), event.y())

    def mouseReleaseEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        self._USER_REGION_PLACER.end_detection_region_creation()

