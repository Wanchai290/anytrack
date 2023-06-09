from PySide6.QtWidgets import QMenu, QWidget

from pattern_tracking.proper.logic.VideoReader import VideoReader
from pattern_tracking.proper.qt_gui.top_menu_bar.video.SelectVideoAction import SelectVideoAction


class VideoMenu(QMenu):

    def __init__(self, live_feed: VideoReader, parent: QWidget | None = None):
        super().__init__(parent)

        self._SELECT_VIDEO_ACTION = SelectVideoAction(live_feed)

        self.addAction(self._SELECT_VIDEO_ACTION)
        self.setTitle("Video")


