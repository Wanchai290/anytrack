import socket
import time
from queue import Queue
from threading import Event, Thread
from typing import Callable

from numpy import ndarray

from raspberry_communication_protocol.Packet import Packet
from raspberry_communication_protocol.PacketHandler import PacketHandler
from raspberry_communication_protocol.PacketType import PacketType


class FrameTCPClient:

    MAX_TIMEOUT_S = 999

    def __init__(self, host: str, port: int, halt: Event):
        self.received_frames_queue: Queue[tuple[int, ndarray]] = Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self._halt_event = halt
        self._thread = Thread(target=self.run)

    def ask_for_new_frame(self):
        p = Packet.placeholder()
        p.packet_type = PacketType.OK
        self.socket.send(p.serialize())

    def request_same_frame_again(self):
        p = Packet.placeholder()
        p.packet_type = PacketType.REQUEST
        self.socket.send(p.serialize())

    def end_connection(self):
        p = Packet.placeholder()
        p.packet_type = PacketType.HALT
        self.socket.send(p.serialize())

    def read_response(self) -> Packet:
        response = PacketHandler.read_start_word(self.socket)
        if response is not None:
            response += PacketHandler.read_until_end_word(self.socket, time.time(), FrameTCPClient.MAX_TIMEOUT_S)
        return Packet.deserialize(response)

    def run(self):
        ask_method: Callable[[None], None] = self.ask_for_new_frame
        while not self._halt_event.is_set():
            # this line was here for testing purposes
            self._halt_event.set()
            ask_method()
            packet = self.read_response()
            if packet.is_valid():
                self.received_frames_queue.put((packet.frame_number, packet.payload))
                ask_method = self.ask_for_new_frame
            else:
                ask_method = self.request_same_frame_again
        self.end_connection()

    def run_forever(self):
        self._thread.start()
