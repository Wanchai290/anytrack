from abc import ABC, abstractmethod
from queue import Queue
from threading import Event

import numpy as np


class AbstractFrameProvider(ABC):
    """
    Abstract class responsible for providing frames from a video input.
    To implement this class, you have two choices :

    1. (Preferred method) Override the start() and stop() method, supposed to respectively start or stop
    a background worker, that will put the acquired frame in the self._frames_queue attribute with the
    following format : (frame_number, np.ndarray)

    2. Override the `self.grab_frame()` method to return a new frame. See the documentation of this method
    for more information about this choice.
    """

    def __init__(self, global_halt: Event, is_video: bool, max_frames_in_queue: int = 30):
        self._global_halt = global_halt
        """Global event used to check whether or not to continue working. Not modified by this class"""
        self._stop_working: Event = Event()
        """
        Local event that stops this class' background worker, without stopping other operations
        Used when switching feeds, to avoid deadlocking (i.e. the main thread waits for a frame, but
        this provider stopped working).
        """
        self._is_video = is_video
        """True if the feed is a static video, false if it is live"""
        self._frames_queue: Queue[tuple[int, np.ndarray] | None] = Queue(max_frames_in_queue)
        """The queue containing all the frames grabbed by the reader"""

    @abstractmethod
    def start(self):
        """
        Run this frame provider in the background, to make it acquire frames
        It must put the newly acquired frame in the `self._frames_queue` attribute
        """
        pass

    @abstractmethod
    def stop(self):
        """Stops the background worker. Does NOT update self._global_halt_event"""
        pass

    def grab_frame(self,
                   block: bool | None = None,
                   timeout: float | None = None) -> tuple[int, np.ndarray]:
        """
        Returns the oldest frame obtained from the video feed.
        If the feed has been tasked to stop working, then raise FeedAlreadyStoppedException

        Note: If your override this method, you MUST raise `FeedAlreadyStoppedException`
              in case the feed has already stopped working (if `self._global_halt_event.is_set()`)
        :param block: Blocks until a new frame is available
        :param timeout: If block is True, waits maximum 'timeout' time
        :return: The oldest frame captured
        """
        return self._frames_queue.get(block, timeout)

    def get_global_halt_event(self):
        return self._global_halt
