from src.pattern_tracking.logic.video.AbstractFrameProvider import AbstractFrameProvider


class LiveFeedWrapper:
    """
    Wrapper class for AbstractFrameProvider object
    It was either creating this class, or passing the Main class as an argument
    to all child classes who required the live feed
    """

    def __init__(self, feed: AbstractFrameProvider):
        self._feed = feed

    def start(self):
        self._feed.start()

    def stop(self):
        self._feed.stop()

    def grab_frame(self, block: bool = True):
        return self._feed.grab_frame(block)

    def get_halt_event(self):
        return self._feed.get_halt_event()

    def change_feed(self, feed: AbstractFrameProvider):
        self._feed.stop()
        self._feed = feed
        self._feed.start()
