import logging
from queue import Queue
from socketserver import TCPServer
from threading import Event

from numpy import ndarray


class FrameTCPServer(TCPServer):

    DEFAULT_PORT = 47828
    LOGGER_NAME = "FrameTCPServerLogger"

    def __init__(self, server_address, RequestHandlerClass, frames_queue: Queue[int, ndarray], halt_event: Event):
        super().__init__(server_address, RequestHandlerClass)
        logging.basicConfig(level=logging.NOTSET)
        self._logger = logging.getLogger(FrameTCPServer.LOGGER_NAME)
        self._logger.info(f"Server initialized and bound to {server_address}")
        self.frames_queue = frames_queue
        self.halt_server_event = halt_event
        self.current_data_to_send = None
        self.timeout_timer_start = None

    def get_logger(self):
        return self._logger
