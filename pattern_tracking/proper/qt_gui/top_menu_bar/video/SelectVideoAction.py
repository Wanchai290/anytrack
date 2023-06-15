from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QWidget, QApplication

from pattern_tracking.proper.logic.video.VideoReader import VideoReader


class SelectVideoAction(QAction):

    def __init__(self, live_feed: VideoReader, dialog_parent: QWidget | None = None):
        super().__init__()
        self.triggered.connect(self._select_video_dialog)
        self.setText("Launch from video")
        self._live_feed = live_feed
        self._dialog_parent = dialog_parent

    def _select_video_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self._dialog_parent, "Open video file", filter="Video files (*.avi *.jpg *.mp4)")
        if len(file_name) != 0:
            self._live_feed.change_feed(file_name, is_video=True, loop_video=True)


if __name__ == '__main__':
    app = QApplication()
    o = SelectVideoAction(None)
    o._select_video_dialog()
    app.exec()