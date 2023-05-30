from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import QMainWindow, QMenu

from pattern_tracking.proper.tracker.TrackerManager import TrackerManager
from pattern_tracking.proper.qt_gui.FrameDisplayWidget import FrameDisplayWidget


class AppMainWindow(QMainWindow):
    """
    Main display to the user. Initializes the application
    with the different menus, sidebar menus and buttons
    """

    def __init__(self, tracker_manager: TrackerManager, frame_shape: tuple[int, int, int]):
        super().__init__()

        self._TRACKER_MANAGER = tracker_manager
        self._FRAME_DISPLAY = FrameDisplayWidget(tracker_manager, frame_shape)
        # self._live_dist_plot: QWidget =

        # an example on how to handle QMenuBar, QMenu and QAction objects
        self.setCentralWidget(self._FRAME_DISPLAY)
        menu = self.menuBar().addMenu("File")
        save = QAction("Save", self)
        save.triggered.connect(lambda: print("hi"))
        menu.addAction(save)

    def get_frame_display_widget(self) -> FrameDisplayWidget:
        return self._FRAME_DISPLAY
