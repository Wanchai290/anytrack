from threading import Event, Thread

import zmq

from src.comm_protocol.Packet import Packet
from src.pattern_tracking.logic.video.AbstractFrameProvider import AbstractFrameProvider


class FramesFromZMQSocket(AbstractFrameProvider):
    """
    Retrieves image frames in the format defined in `Packet.py`
    from a distant ZMQ socket via TCP.
    Connection is initialized on object creation.
    """

    DEFAULT_PORT = 47828

    def __init__(self, ip_address: str, port: int,
                 global_halt: Event, max_frames_in_queue: int = 30):
        super().__init__(global_halt, False, max_frames_in_queue)
        self._zmq_context = zmq.Context()
        self._socket = self._zmq_context.socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self._socket.connect(f"tcp://{ip_address}:{port}")
        self._running = False
        self._thread = Thread(target=self._read_socket_data)

    def start(self):
        self._running = True
        self._thread.start()

    def _read_socket_data(self):
        while self._running and not self._global_halt.is_set():
            raw_data = self._socket.recv()
            packet = Packet.deserialize(raw_data)
            if packet is not None:
                self._frames_queue.put((packet.frame_number, packet.payload))

        self._zmq_context.destroy()
        self._running = False

    def stop(self):
        self._running = False
