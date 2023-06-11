from __future__ import annotations

import io
import pickle
from typing import Any

import crc
import numpy as np

from raspberry_communication_protocol.PacketType import PacketType


class Packet:
    """
    Content description of a packet that implements
    a custom Application Layer communication protocol

    Attributes:
        - self._frame_id: 16 bits length, the ID of the frame
        - self._packet_type: 2 bits length, type of packet sent
        - self._payload: Arbitrary length, the NumPy array containing the frame
        - self._payload_crc: CRC checksum of the payload
    """
    # note: there was no proper choice when choosing the polynomial here, it's just to have a CRC to check for
    CRC_COMPUTER = crc.Calculator(crc.Crc16.CCITT.value)

    # Defining the protocol's values here.
    PROTOCOL_VER = b"01"
    LEN_PROTOCOL_VER = 2  # bits (binary)

    START_MAGIC_WORD = b"inu"
    LEN_START_MAGIC_WORD = len(START_MAGIC_WORD)
    END_MAGIC_WORD = b"neko"
    LEN_END_MAGIC_WORD = len(END_MAGIC_WORD)
    LEN_HEADER = LEN_START_MAGIC_WORD + LEN_PROTOCOL_VER

    LEN_FRAME_ID = 16  # Numb
    LEN_PACKET_TYPE = 2
    LEN_PAYLOAD_LENGTH = 24
    LEN_PAYLOAD_CRC = 16  # because we use Crc16

    def __init__(self, frame_id: int, packet_type: PacketType, payload: np.ndarray):
        self.frame_id = frame_id
        self.packet_type = packet_type
        self.payload = payload
        # CRC is computed over packet's unique data
        self.payload_crc = Packet.compute_crc(self)

    def __eq__(self, other):
        if type(other) != Packet:
            return False
        return self.frame_id == other.frame_id \
            and self.packet_type == other.packet_type \
            and (self.payload == other.payload).all() \
            and self.payload_crc == other.payload_crc

    def is_valid(self):
        """Returns True if the packet is correctly formatted. Does not check protocol version mismatch !"""
        if self.frame_id.bit_length() > 4 and type(self.packet_type) != PacketType:
            return False

        # Can't compute the payload of the NumPy array directly, we need its binary representation
        return Packet.compute_crc(self) == self.payload_crc

    def serialize(self) -> bytes:
        """Serialize this packet's content and returns the binary string"""
        data = Packet.START_MAGIC_WORD
        data += Packet.PROTOCOL_VER
        data += hex(self.frame_id).zfill(Packet.LEN_FRAME_ID)
        data += bytes(self.packet_type.value).zfill(Packet.LEN_PACKET_TYPE)

        bytes_payload = self.payload.tobytes()  # C order for the NumPy array by default
        payload_length = len(bytes_payload)
        data += bytes(payload_length).zfill(24)
        data += bytes_payload

        data += bytes(self.payload_crc)
        data += Packet.END_MAGIC_WORD

        return data

    @staticmethod
    def compute_crc(packet: Packet):
        """Computes and returns the payload's CRC when saved using np.save()"""
        return Packet.CRC_COMPUTER.checksum(bytes(packet.payload))

    @classmethod
    def new_empty(cls) -> Packet:
        return Packet(-1, PacketType.OK, np.array(()))

    @staticmethod
    def deserialize(packet: bytes) -> Packet | None:
        """Deserializes a packet, and returns a Packet object"""
        deserialized = Packet.new_empty()
        # check for magic word and protocol ver
        if packet[:Packet.LEN_START_MAGIC_WORD] != Packet.START_MAGIC_WORD \
                or packet[
                   Packet.LEN_START_MAGIC_WORD:
                   Packet.LEN_START_MAGIC_WORD+Packet.LEN_PROTOCOL_VER
                   ] != Packet.PROTOCOL_VER:
            return
        packet = packet[Packet.LEN_HEADER:]  # truncate for a bit more readability

        # I am pretty sure you can create a weird loop with a dict
        # to automate that kind of things
        # this looks disgusting, but IDK how to make it better
        deserialized.frame_id = int(packet[:Packet.LEN_FRAME_ID])
        packet = packet[Packet.LEN_FRAME_ID:]

        deserialized.packet_type = int(packet[:Packet.LEN_PACKET_TYPE])
        packet = packet[Packet.LEN_PACKET_TYPE:]

        payload_length = int(packet[:Packet.LEN_PAYLOAD_LENGTH - 1])
        deserialized.payload = packet[Packet.LEN_PAYLOAD_LENGTH: payload_length - 1]
        packet = packet[Packet.LEN_PAYLOAD_LENGTH + payload_length:]

        if packet[:Packet.LEN_END_MAGIC_WORD - 1] != Packet.END_MAGIC_WORD:
            return

        return deserialized

if __name__ == '__main__':
    p = Packet(0xFA, PacketType.FRAME, np.array((5, 6)))
    s = p.serialize()
    pds = Packet.deserialize(s)
    print(pds.is_valid())
