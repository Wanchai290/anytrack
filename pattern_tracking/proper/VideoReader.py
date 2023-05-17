from queue import Queue
from threading import Thread, Event

import cv2 as cv
import numpy as np


class VideoReader:
    def __init__(self, camera_feed: str | int,
                 is_video: bool,
                 halt_work: Event,
                 max_frames_in_queue: int = 30):

        self.__video_feed: cv.VideoCapture = cv.VideoCapture(camera_feed)
        if not self.__video_feed.isOpened():
            raise IOError("Couldn't open video feed !")

        self.__frames_queue: Queue = Queue(max_frames_in_queue)
        self.__is_video = is_video
        self.__stop_event = halt_work

        self.__thread: Thread | None = None

    def run_threaded(self):
        """
        Reads & places all grabbed frames in a queue of the object
        :return:
        """
        self.__thread = Thread(target=self.async_process,
                               args=(self.__video_feed, self.__frames_queue, self.__stop_event))
        self.__thread.start()

    def join_process(self, timeout: int = None):
        """
        Waits for the main processing thread to
        :param timeout: Maximum time out to wait for
        """
        if self.__thread.is_alive():
            self.__thread.join(timeout if timeout is not None else 0)

    @staticmethod
    def async_process(video: cv.VideoCapture, w_read_frames_q: Queue[tuple[int, cv.Mat]],
                      halt_event: Event):
        """
        TODO: put in utils ?
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
        self.__stop_event.set()

    def grab_frame(self,
                   block: bool | None = None,
                   timeout: float | None = None) -> tuple[int, np.ndarray]:
        return self.__frames_queue.get(block, timeout)
