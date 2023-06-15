from typing import Callable

from pattern_tracking.proper.logic.video.FramesFromDistantServer import FramesFromDistantServer
from pattern_tracking.proper.logic.video.VideoReader import VideoReader


class LiveFeedWrapper:
    """
    Wrapper class for AbstractFrameProvider object
    It was either creating this class, or passing the Main class as an argument
    to all child classes who required the live feed
    """

    def __init__(self, feed: VideoReader | FramesFromDistantServer):
        self._feed = feed

    def start(self):
        self._feed.start()

    def grab_frame(self, block: bool = True):
        return self._feed.grab_frame(block)

    def get_halt_event(self):
        return self._feed.get_halt_event()

    def change(self, feed: VideoReader | FramesFromDistantServer):
        self._feed = feed
        self._feed.start()
