from abc import ABC, abstractmethod
from queue import Queue
from threading import Event

import numpy as np


class AbstractFrameProvider(ABC):

    def __init__(self, halt_event: Event, is_video: bool, max_frames_in_queue: int = 30):
        self._halt_event = halt_event
        """Event used to check whether or not to continue working"""
        self._is_video = is_video
        """True if the feed is a static video, false if it is live"""
        self._frames_queue: Queue[tuple[int, np.ndarray] | None] = Queue(max_frames_in_queue)
        """The queue containing all the frames grabbed by the reader"""

    @abstractmethod
    def start(self):
        """Run this frame provider in the background, to make it acquire frames"""
        pass

    @abstractmethod
    def stop(self):
        pass

    def grab_frame(self,
                   block: bool | None = None,
                   timeout: float | None = None) -> tuple[int, np.ndarray]:
        """Returns the oldest frame obtained from the feed"""
        return self._frames_queue.get(block, timeout)

    def get_halt_event(self):
        return self._halt_event
