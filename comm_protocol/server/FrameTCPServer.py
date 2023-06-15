from queue import Queue
from socketserver import TCPServer

from numpy import ndarray


class FrameTCPServer(TCPServer):

    DEFAULT_PORT = 47827

    def __init__(self, frames_queue: Queue[int, ndarray], *args):
        super().__init__(*args)
        self.frames_queue = frames_queue
        self.current_data_to_send = None
        self.timeout_timer_start = None
