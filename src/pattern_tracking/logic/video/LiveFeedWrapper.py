import time

from src.pattern_tracking.logic.video.AbstractFrameProvider import AbstractFrameProvider
from src.pattern_tracking.logic.video.DummyVideoFeed import DummyVideoFeed


class LiveFeedWrapper:
    """
    Wrapper class for AbstractFrameProvider object.
    It was either creating this class, or passing the Main class as an argument
    to all child classes who required the live feed

    Whenever we want to change the video input, this object replaces its self._feed attribute
    and replaces it with a new instance of `AbstractFrameProvider`
    """

    def __init__(self, feed: AbstractFrameProvider):
        self._feed = feed

    def start(self):
        self._feed.start()

    def stop(self):
        self._feed.stop()

    def grab_frame(self, block: bool = False, timeout: float = 0.01):
        return self._feed.grab_frame(block, timeout)

    def get_global_halt_event(self):
        return self._feed.get_global_halt_event()

    def change_feed(self, feed: AbstractFrameProvider):
        """
        Changes the current video input feed by another valid one.
        :param feed: The video feed object, child of AbstractFrameProvider
        """
        self._feed.stop()
        self._feed = feed
        self._feed.start()
