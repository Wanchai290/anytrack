from __future__ import annotations

import struct

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
    CRC_COMPUTER = crc.Calculator(crc.Crc8.CCITT.value)

    # Defining the protocol's values here.
    PROTOCOL_VER = 0b10

    START_MAGIC_WORD = b"inu"
    END_MAGIC_WORD = b"neko"

    LEN_PAYLOAD_CRC = 8  # because we use Crc8

    def __init__(self, frame_id: int, packet_type: PacketType, payload: np.ndarray):
        self.frame_id = frame_id
        self.packet_type = packet_type
        self.payload = payload
        # CRC is computed over packet's unique data
        self.payload_crc = Packet.compute_crc(self)

    def payload_length(self):
        return len(self.payload.tobytes())

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
        # We concat ProtocolVer and PacketType to save some space and use only a single byte for their storage
        # Please check `comm_protocol_definition.md` for more details
        proto_and_ptype = (Packet.PROTOCOL_VER << 2 | self.packet_type.value) << 4
        proto_and_ptype_bytes = proto_and_ptype.to_bytes(1, "big")

        # Compute payload length to find the shape of the format
        # to use with struct.pack()
        payload_length = self.payload_length()
        payload_length_format = f"{payload_length}s"
        data = struct.pack(
            "!3sciI" + payload_length_format + f"{Packet.LEN_PAYLOAD_CRC}s" + "4s",
            Packet.START_MAGIC_WORD,
            proto_and_ptype_bytes,
            self.frame_id,
            self.payload_length(),
            self.payload.tobytes(),
            self.payload_crc.to_bytes(Packet.LEN_PAYLOAD_CRC, byteorder="little"),
            Packet.END_MAGIC_WORD
        )
        print(data)
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
        # deserialized = Packet.new_empty()
        # # check for magic word and protocol ver
        # if packet[:Packet.LEN_START_MAGIC_WORD] != Packet.START_MAGIC_WORD \
        #         or packet[
        #            Packet.LEN_START_MAGIC_WORD:
        #            Packet.LEN_START_MAGIC_WORD+Packet.LEN_PROTOCOL_VER
        #            ] != Packet.PROTOCOL_VER:
        #     return
        # packet = packet[Packet.LEN_HEADER:]  # truncate for a bit more readability
        #
        # # I am pretty sure you can create a weird loop with a dict
        # # to automate that kind of things
        # # this looks disgusting, but IDK how to make it better
        # deserialized.frame_id = int(packet[:Packet.LEN_FRAME_ID])
        # packet = packet[Packet.LEN_FRAME_ID:]
        #
        # deserialized.packet_type = int(packet[:Packet.LEN_PACKET_TYPE])
        # packet = packet[Packet.LEN_PACKET_TYPE:]
        #
        # payload_length = int(packet[:Packet.LEN_PAYLOAD_LENGTH - 1])
        # deserialized.payload = packet[Packet.LEN_PAYLOAD_LENGTH: payload_length - 1]
        # packet = packet[Packet.LEN_PAYLOAD_LENGTH + payload_length:]
        #
        # if packet[:Packet.LEN_END_MAGIC_WORD - 1] != Packet.END_MAGIC_WORD:
        #     return
        #
        # return deserialized


if __name__ == '__main__':
    p = Packet(0xFA, PacketType.FRAME, np.array((5, 6)))
    s = p.serialize()
    pds = Packet.deserialize(s)
    print(pds.is_valid())
