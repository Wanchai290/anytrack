from PySide6.QtGui import QAction

from pattern_tracking.proper.logic.VideoReader import VideoReader


class SelectCameraAsLiveFeedAction(QAction):
    
    def __init__(self, live_feed: VideoReader):
        super().__init__()
        self._live_feed = live_feed
        self.triggered.connect(self._set_camera_as_live_feed)
        self.setText("Use live camera feed")
    def _set_camera_as_live_feed(self):
        self._live_feed.change_feed(0, is_video=False)
