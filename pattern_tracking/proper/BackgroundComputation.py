from threading import Event, Thread

from pattern_tracking.proper.TrackerManager import TrackerManager
from pattern_tracking.proper.VideoReader import VideoReader
from pattern_tracking.proper.qt_gui.FrameDisplayWidget import FrameDisplayWidget


class BackgroundComputation:

    def __init__(self,
                 tracker_manager: TrackerManager,
                 live_feed: VideoReader,
                 frame_display_widget: FrameDisplayWidget,
                 halt_event: Event):
        self._TRACKER_MANAGER = tracker_manager
        self._LIVE_FEED = live_feed
        self._frame_display_widget = frame_display_widget
        self._halt = halt_event
        self._thread: Thread | None = None

    def run(self):
        while not self._halt.is_set():
            live_frame = self._LIVE_FEED.grab_frame(block=True)[1]
            edited_frame = self._TRACKER_MANAGER.update_trackers(live_frame, drawing_sheet=live_frame.copy())
            self._frame_display_widget.change_frame_to_display(edited_frame, swap_rgb=True)

    def run_threaded(self):
        self._thread = Thread(target=self.run, args=())
        self._thread.start()
