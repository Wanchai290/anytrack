import os
import queue
import time
from threading import Thread, Event

import numpy as np
from PIL import Image

from src.pattern_tracking.logic.video.AbstractFrameProvider import AbstractFrameProvider


class DummyVideoFeed(AbstractFrameProvider):
    """
    This dummy class is used during startup to provide an empty object
    to the LiveFeedWrapper. It gets replaced with a proper implementation
    when the user selects a proper video input source.
    """

    PAUSE_BEFORE_NEXT_FRAME = 0.25

    def __init__(self, global_halt: Event):
        super().__init__(global_halt, False)
        self._static_frames: list[np.ndarray] = []
        self._thread: Thread | None = None

    def _load_static_frames(self):
        with os.scandir(os.path.abspath('../../assets/dummy_feed_frames/')) as directory:
            for obj in directory:
                if obj.is_file():
                    self._static_frames.append(
                        np.array(
                            Image.open(obj.path)
                        )
                    )

    def _run(self):
        frame_num = 0
        current_frame_index = 0
        while not self._stop_working.is_set() and not self._global_halt.is_set():
            try:
                self._frames_queue.put(
                    (frame_num, self._static_frames[current_frame_index]),
                    block=False, timeout=0.5
                )
            except queue.Full:
                continue
            frame_num += 1
            current_frame_index = 0 if current_frame_index >= len(self._static_frames) - 1 else current_frame_index + 1
            time.sleep(DummyVideoFeed.PAUSE_BEFORE_NEXT_FRAME)

    def start(self):
        self._load_static_frames()
        self._thread = Thread(target=self._run)
        self._thread.start()
        
    def stop(self):
        self._stop_working.set()
