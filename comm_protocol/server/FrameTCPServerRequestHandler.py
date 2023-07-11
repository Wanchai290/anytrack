import logging
import time
from socketserver import BaseRequestHandler

from comm_protocol.Packet import Packet
from comm_protocol.PacketHandler import PacketHandler
from comm_protocol.PacketType import PacketType


class FrameTCPServerRequestHandler(BaseRequestHandler):
    """
    The handler class for the FrameTCPServer class.
    Only meant for use with the mentioned class
    """

    MAX_READ_TIMEOUT_S = 30
    """Max allowed timeout in seconds"""

    def handle(self) -> None:
        logger: logging.Logger = self.server.get_logger()
        logger.info("Connection started")
        while True:
            logger.info("Reading connection buffer")
            self.server.timeout_timer_start = time.time()
            data = PacketHandler.read_start_word(self.request, logger)
            if data is None:
                logger.info("Start word is not correct, reading again")
                continue

            logger.info("Valid start word, continuing read")
            rest_data = PacketHandler.read_until_end_word(self.request, self.server.timeout_timer_start,
                                                          FrameTCPServerRequestHandler.MAX_READ_TIMEOUT_S)
            if rest_data is None:
                logger.warning("Rest of data was invalid, packet must have been corrupted")
                continue

            # read the other end's request
            logger.info("Full packet correctly received")
            logger.info("Deserializing packet")
            deserialized = Packet.deserialize(data + rest_data)
            logger.info(f"PacketType : {deserialized.packet_type}")
            if deserialized.packet_type == PacketType.OK:
                logger.info("Retrieving new frame from queue and sending it")
                # Actualize the data we have to send, then send it right away
                self.server.current_data_to_send = self.server.frames_queue.get(block=True)
                logger.info("Obtained new frame from queue, sending")
                self._send_current_data()
            elif deserialized.packet_type == PacketType.REQUEST:
                logger.info("Re-sending current frame")
                # The other end didn't receive the packet correctly, re-sending the data
                self._send_current_data()
            elif deserialized.packet_type == PacketType.HALT:
                logger.info("Halt requsted, closing...")
                # Sever the connection
                # self.server.socket.close()
                self.server.shutdown()

    def _send_current_data(self):
        """Sends a packet frame to the other end"""
        frame_number, image = self.server.current_data_to_send
        packet = Packet(frame_number, PacketType.FRAME, image)
        self.request.sendall(packet.serialize())
