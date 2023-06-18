from threading import Event, Thread
import cv2 as cv

from pattern_tracking.proper.logic.tracker.TrackerManager import TrackerManager
from pattern_tracking.proper.logic.video.LiveFeedWrapper import LiveFeedWrapper
from pattern_tracking.proper.qt_gui.widgets.FrameDisplayWidget import FrameDisplayWidget
from pattern_tracking.proper.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget


class BackgroundComputation:

    def __init__(self,
                 tracker_manager: TrackerManager,
                 live_feed: LiveFeedWrapper,
                 frame_display_widget: FrameDisplayWidget,
                 plots_container: LivePlotterDockWidget,
                 halt_event: Event):
        self._TRACKER_MANAGER = tracker_manager
        self._LIVE_FEED = live_feed
        self._FRAME_DISPLAY_WIDGET = frame_display_widget
        self._PLOTS_CONTAINER_WIDGET = plots_container
        self._halt = halt_event
        self._thread: Thread | None = None

    def _run(self):
        """
        Continuously processes data to be displayed
        This method shouldn't be launched as is, but from a separate thread only
        """
        while not self._halt.is_set():
            frame_number, live_frame = self._LIVE_FEED.grab_frame(block=True)
            resized_frame = cv.resize(live_frame, FrameDisplayWidget.WIDGET_SIZE)
            edited_frame = self._TRACKER_MANAGER.update_trackers(resized_frame, drawing_sheet=resized_frame.copy())
            self._PLOTS_CONTAINER_WIDGET.update_plots(frame_number)
            self._FRAME_DISPLAY_WIDGET.change_frame_to_display(edited_frame, swap_rgb=True)

    def start(self):
        """Starts this class' job in the background"""
        self._thread = Thread(target=self._run, args=())
        self._thread.start()
