import time
from numpy import ndarray
from queue import Queue
from socketserver import BaseRequestHandler

from raspberry_communication_protocol.Packet import Packet
from raspberry_communication_protocol.PacketHandler import PacketHandler
from raspberry_communication_protocol.PacketType import PacketType


class FrameTCPServerRequestHandler(BaseRequestHandler):
    """
    The handler class for the FrameTCPServer class.
    Only meant for use with the mentioned class
    """

    # MAX_READ_TIMEOUT_S = 1
    MAX_READ_TIMEOUT_S = 100000
    """Max allowed timeout in seconds"""

    def handle(self) -> None:
        self.server.timeout_timer_start = time.time()
        data = PacketHandler.read_start_word(self.request)
        if data is None:
            return

        rest_data = PacketHandler.read_until_end_word(self.request, self.server.timeout_timer_start,
                                                      FrameTCPServerRequestHandler.MAX_READ_TIMEOUT_S)
        if rest_data is None:
            return

        # read the other end's request
        deserialized = Packet.deserialize(data + rest_data)
        if deserialized.packet_type == PacketType.OK:
            # Actualize the data we have to send, then send it right away
            self.server.current_data_to_send = self.server.frames_queue.get(block=True)
            self._send_current_data()
        elif deserialized.packet_type == PacketType.REQUEST:
            # The other end didn't receive the packet correctly, re-sending the data
            self._send_current_data()
        elif deserialized.packet_type == PacketType.HALT:
            # Sever the connection
            # self.server.socket.close()
            self.server.shutdown()

    def _send_current_data(self):
        """Sends a packet frame to the other end"""
        frame_number, payload = self.server.current_data_to_send
        packet = Packet(frame_number, PacketType.FRAME, payload)
        self.request.sendall(packet.serialize())
