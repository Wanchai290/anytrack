from queue import Queue
from threading import Thread, Event

import cv2 as cv
import numpy as np


class VideoReader:
    """
    Continuously reads frames from a video file
    or from a video feed, and puts them in a readable
    queue, alongside the frame number
    """
    def __init__(self, camera_feed: str | int,
                 is_video: bool,
                 halt_work: Event,
                 max_frames_in_queue: int = 30):

        self._video_feed: cv.VideoCapture = cv.VideoCapture(camera_feed)
        """Video feed"""

        self._frames_queue: Queue[tuple[int, np.ndarray] | None] = Queue(max_frames_in_queue)
        """The queue containing all the frames grabbed by the video reader"""
        self._is_video = is_video
        """True if the feed is a static video, false if it is live"""
        self._stop_event = halt_work
        """Event used to check whether or not to continue working"""

        self._thread: Thread | None = None
        """The thread used to process frames in the background"""

        if not self._video_feed.isOpened():
            raise IOError("Couldn't open video feed !")

    def run_threaded(self):
        """
        Reads & places all grabbed frames in a queue of the object
        """
        self._thread = Thread(target=self.async_process,
                              args=(self._video_feed, self._frames_queue, self._stop_event))
        self._thread.start()

    def join_process(self, timeout: int = None):
        """
        Waits for the background processing thread to finish
        :param timeout: Maximum time out to wait for
        """
        if self._thread.is_alive():
            self._thread.join(timeout if timeout is not None else 0)

    @staticmethod
    def async_process(video: cv.VideoCapture, w_read_frames_q: Queue[tuple[int, cv.Mat]],
                      halt_event: Event):
        """
        Thread-safe video reader method
        Opens a video file (or video capture device feed),
        then continuously reads the frames of the video and stores them in a queue

        Data format of the items that are written to the queue are as follows :
        tuple[int, cv.Mat]|None
        """
        frame_id = 0
        while video.isOpened() and not halt_event.is_set():
            ret, frame = video.read()
            if not ret:
                break

            w_read_frames_q.put((frame_id, frame))
            frame_id += 1

        halt_event.set()

    def force_halt(self):
        """
        Forcefully sets the stop Event object to halt
        any work being done. This will affect other processes
        using the same Event object as well
        """
        self._stop_event.set()

    def grab_frame(self,
                   block: bool | None = None,
                   timeout: float | None = None) -> tuple[int, np.ndarray]:
        """Returns the oldest frame obtained from the video feed"""
        return self._frames_queue.get(block, timeout)
