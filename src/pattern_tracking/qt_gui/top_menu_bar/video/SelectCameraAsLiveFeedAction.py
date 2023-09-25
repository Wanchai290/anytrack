from PySide6.QtGui import QAction

from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.logic.video.VideoReader import VideoReader
from src.pattern_tracking.shared import utils


class SelectCameraAsLiveFeedAction(QAction):
    
    def __init__(self, live_feed: LiveFeedWrapper):
        super().__init__()
        self._live_feed = live_feed
        self.triggered.connect(self._set_camera_as_live_feed)
        self.setText("Use live camera feed")

    def _set_camera_as_live_feed(self):
        _, working_ports, _ = utils.opencv_list_available_camera_ports()
        if type(self._live_feed == VideoReader):
            self._live_feed.change_feed(working_ports[0], is_video=False)
        else:
            self._live_feed = VideoReader(working_ports[0],
                                          halt_work=self._live_feed.get_halt_event(),
                                          is_video=False)
