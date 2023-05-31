import PySide6.QtCore
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QMessageBox

import numpy as np

from pattern_tracking.proper.shared import utils
from pattern_tracking.proper.tracker.TrackerManager import TrackerManager
from pattern_tracking.proper.qt_gui.logic.UserRegionPlacer import UserRegionPlacer


class FrameDisplayWidget(QLabel):
    """
    QT widget displaying the most recent available frame,
    on which is highlighted the current region of interests
    being tracked.

    This widget only displays given frames, and does not compute which
    areas to highlight to locate the tracked objects. The latter computation
    is done in the BackgroundComputation class.

    The logic to know whether to call the bindings or not is performed in this object
    Updates to the region of interest or trackers is done in the UserRegionPlacer object
    """

    def __init__(self, tracker_manager: TrackerManager, frames_shape: tuple):
        super().__init__()

        # Disable resize of this widget
        self.setFixedSize(*frames_shape[1::-1])  # In OpenCV, shape is as follows : (height, width, depth)

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

        self._frame_pixmap = utils.ndarray_to_qimage(np.zeros(frames_shape), as_qpixmap=True)
        """The QPixmap variant of the current frame displayed. This is the object that Qt displays"""

        self.setPixmap(self._frame_pixmap)

    def get_current_frame(self):
        """Returns the backing NumPy array image displayed to the user"""
        return self._current_frame

    def get_active_selected_tracker(self):
        """Returns the current active selected tracker, or None if there isn't any selected"""
        if self._check_current_active_tracker_valid():
            return self._tracker_manager.get_active_selected_tracker()
        else:
            return None

    def _check_current_active_tracker_valid(self):
        """
        Checks whether a currently active tracker exists,
        displays a warning message box if there is None available

        dev note: it was necessary to duplicate the call to this method multiple times
        because of the way we redefine mouse events with PySide6
        """
        try:
            self._tracker_manager.get_active_selected_tracker()
        except ValueError:
            alert = QMessageBox(self)
            alert.setWindowTitle("No trackers defined !")
            alert.setText("You need to create at least one tracker to start "
                          "tracking on the current video feed !\n\n"
                          "Click on the \"Trackers\" tab in the top-left "
                          "to create a new one")
            alert.exec()
            return False
        return True

    # -- Mouse events binding
    # We override Qt's mouse interaction methods to manage our events

    def change_frame_to_display(self, frame: np.ndarray, swap_rgb: bool = False):
        """
        Updates the current image displayed by this QLabel,
        by converting the passed NumPy frame as a QPixmap

        :param frame: The frame to be displayed
        :param swap_rgb: True if we have to swap the RGB order of the image
                         Often necessary when working with OpenCV for example
        """
        self._current_frame = frame
        q_img = utils.ndarray_to_qimage(frame, swap_rgb, as_qpixmap=True)
        self.setPixmap(q_img)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self._check_current_active_tracker_valid():
            return

        if event.button() == PySide6.QtCore.Qt.MouseButton.LeftButton:
            self._USER_REGION_PLACER.create_new_poi(
                self.get_active_selected_tracker(),
                event.x(),
                event.y()
            )

        elif event.button() == PySide6.QtCore.Qt.MouseButton.RightButton:
            self._USER_REGION_PLACER.create_new_detection_region(event.x(), event.y())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._check_current_active_tracker_valid():
            return

        if self._USER_REGION_PLACER.drawing():
            self._USER_REGION_PLACER.update_detection_region_end(event.x(), event.y())

    def mouseReleaseEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        if not self._check_current_active_tracker_valid():
            return

        self._USER_REGION_PLACER.end_detection_region_creation()
