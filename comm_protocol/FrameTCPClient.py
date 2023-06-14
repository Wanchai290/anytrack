import logging
import socket
import time
from queue import Queue
from threading import Event, Thread
from typing import Callable

from numpy import ndarray

from comm_protocol.Packet import Packet
from comm_protocol.PacketHandler import PacketHandler
from comm_protocol.PacketType import PacketType


class FrameTCPClient:

    MAX_TIMEOUT_S = 999
    LOGGER_NAME = "FrameTCPClientLogger"

    def __init__(self, host: str, port: int, halt: Event, connection_ended_event: Event):
        logging.basicConfig(level=logging.NOTSET)
        self.received_frames_queue: Queue[tuple[int, ndarray]] = Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self._logger = logging.getLogger(FrameTCPClient.LOGGER_NAME)
        self._logger.log(logging.INFO, "Client: Connection initialized.")
        self._halt_event = halt
        self._thread = Thread(target=self.run)
        self._force_stop = False
        self._connection_ended_event = connection_ended_event

    def ask_for_new_frame(self):
        self._logger.log(logging.INFO, "Client: Received frame correctly, asking for another")
        p = Packet.placeholder()
        p.packet_type = PacketType.OK
        self.socket.send(p.serialize())

    def request_same_frame_again(self):
        self._logger.log(logging.WARN, "Client: Erroneous frame, requesting again")
        p = Packet.placeholder()
        p.packet_type = PacketType.REQUEST
        self.socket.send(p.serialize())

    def end_connection(self):
        self._logger.log(logging.INFO, "Client : Sending end of connection")
        p = Packet.placeholder()
        p.packet_type = PacketType.HALT
        self.socket.send(p.serialize())
        self.socket.close()
        self._logger.log(logging.INFO, "Client : Closing socket")
        self._connection_ended_event.set()

    def read_response(self) -> Packet:
        start = PacketHandler.read_start_word(self.socket)
        if start is not None:
            response = start + PacketHandler.read_until_end_word(self.socket, time.time(), FrameTCPClient.MAX_TIMEOUT_S)
            return Packet.deserialize(response)

    def run(self):
        try:
            ask_method: Callable[[None], None] = self.ask_for_new_frame
            while not self._halt_event.is_set() and not self._force_stop:
                ask_method()
                packet = self.read_response()
                if packet is None:
                    # No response at the moment, wait for it to arrive
                    ask_method = lambda: None
                elif packet.is_valid():
                    # Read the frame and put it in the queue
                    self.received_frames_queue.put((packet.frame_number, packet.payload))
                    ask_method = self.ask_for_new_frame
                else:
                    # Ask for the frame again
                    ask_method = self.request_same_frame_again
            self.end_connection()
        except BrokenPipeError:
            self._logger.log(logging.INFO, "Connection ended abruptly, stopping..")
            self._connection_ended_event.set()

    def run_forever(self):
        self._logger.log(logging.INFO, "Client: Started")
        self._thread.start()

    def force_stop(self):
        self._logger.log(logging.INFO, "Client: Forced stop requested")
        self._force_stop = True
