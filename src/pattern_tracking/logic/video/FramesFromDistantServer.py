from threading import Event

from src.comm_protocol.FrameTCPClient import FrameTCPClient
from src.pattern_tracking.logic.video.AbstractFrameProvider import AbstractFrameProvider


class FramesFromDistantServer(AbstractFrameProvider):
    
    def __init__(self, ip_address: str, port: int, global_halt: Event, max_frames_in_queue: int = 30):
        super().__init__(global_halt, False, max_frames_in_queue)
        self._conn_ended = Event()
        self._client = FrameTCPClient(ip_address, port, global_halt, self._conn_ended)
        self._frames_queue = self._client.received_frames_queue

    def start(self):
        self._client.run_forever()

    def stop(self):
        self._client.force_stop()
