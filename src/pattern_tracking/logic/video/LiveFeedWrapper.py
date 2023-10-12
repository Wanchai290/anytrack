from threading import Lock

from src.pattern_tracking.logic.video.AbstractFrameProvider import AbstractFrameProvider


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
        self._reset_feed_mutex = Lock()

    def start(self):
        self._feed.start()

    def stop(self):
        self._feed.stop()

    def grab_frame(self, block: bool = True, timeout: float = 0.5):
        """Wrapper for AbstractFrameProvider.grab_frame() instance method"""
        return self._feed.grab_frame(block, timeout)

    def get_global_halt_event(self):
        return self._feed.get_global_halt_event()

    def change_feed(self, feed: AbstractFrameProvider):
        """
        Changes the current video input feed by another valid one.
        :param feed: The video feed object, child of AbstractFrameProvider
        """
        self._reset_feed_mutex.acquire()
        self._feed.stop()
        self._feed = feed
        self._feed.start()
        # Wait for the feed to start working
        # Technically we don't need it, it's just extra precaution steps
        while self._feed.available_frames() == 0:
            continue
        self._reset_feed_mutex.release()

    def is_feed_resetting(self):
        """
        Returns whether the live feed is currently being changed, i.e.
        the mutex used to change the live feed is locked or not
        """
        return self._reset_feed_mutex.locked()
