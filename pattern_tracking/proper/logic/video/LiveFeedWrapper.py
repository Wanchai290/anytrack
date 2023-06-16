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

    def change_feed(self, feed_origin: str | int, is_video: bool, loop_video: bool = False):
        self._feed.change_feed(feed_origin, is_video, loop_video)

    def change_feed_to_server(self, feed: FramesFromDistantServer):
        self._feed = feed
        self._feed.start()
