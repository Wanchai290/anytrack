from __future__ import annotations

import struct

import crc
import numpy as np

from raspberry_communication_protocol.PacketType import PacketType


class Packet:
    """
    Content description of a packet that implements
    a custom Application Layer communication protocol.

    We use this class to be able to send NumPy array, representing video frames,
    from one computer to another. The base usage was a RaspberryPi grabbing video frames,
    and sending them over Ethernet.

    Please read the given md file for more information on this protocol
    """
    # Frames can get corrupted during transport because of their size.
    # A 16-bit CRC should cover enough unique values for integrity checks
    CRC_COMPUTER = crc.Calculator(crc.Crc16.CCITT.value)

    # Defining the protocol's values here. Sizes are defined in number of **bytes** unless mentioned otherwise
    PROTOCOL_VER = 0b10

    START_MAGIC_WORD = b"inu"
    END_MAGIC_WORD = b"neko"

    LEN_START_MAGIC_WORD = len(START_MAGIC_WORD)
    LEN_PROVER_PTYPE_CCOUNT = 1  # Protocol version, PacketType, Channel count and padding
    LEN_FRAME_NUMBER = 4
    """Number of bytes used for the number that specifies what is
    the current number of the frame"""
    LEN_FRAME_XY_SHAPE = 4
    """Number of bytes for the x and y shape of the video frame (2 bytes each)"""
    LEN_PAYLOAD_LENGTH = 4
    # actual payload's length is computed during runtime
    LEN_PAYLOAD_CRC = 2  # because we use Crc16
    LEN_END_MAGIC_WORD = len(END_MAGIC_WORD)

    # Format string used during serialization
    # Specifies the type of the objects sent, the first character defines the endianness
    # Read the official documentation of struct.pack() for more details
    # You need to update it according to the above ! Otherwise, tests will fail !
    PACKING_FORMAT_START = \
        "!" \
        f"{LEN_START_MAGIC_WORD}s" \
        f"{LEN_PROVER_PTYPE_CCOUNT}c" \
        "I" \
        f"{LEN_FRAME_SHAPE}H" \
        "I"

    PACKING_FORMAT_END = \
        f"{LEN_PAYLOAD_CRC}s" \
        f"{LEN_END_MAGIC_WORD}s"

    def __init__(self, frame_number: int, packet_type: PacketType, payload: np.ndarray):
        self.frame_number = frame_number
        self.packet_type = packet_type
        self.frame_shape = payload.shape[:2]
        if len(payload) <= 2:
            self.frame_channel_count = 1
        else:
            self.frame_channel_count = payload.shape[2]
        self.payload = payload
        # CRC is computed over packet's unique data
        self.payload_crc = Packet.compute_crc(self)

    def payload_length(self):
        """Returns the number of **bytes** required to store this payload."""
        return len(self.payload.tobytes())

    def __eq__(self, other):
        # todo: update
        if type(other) != Packet:
            return False
        return self.frame_number == other.frame_number \
            and self.packet_type == other.packet_type \
            and (self.payload == other.payload).all() \
            and self.payload_crc == other.payload_crc

    def is_valid(self):
        """Returns True if the packet is correctly formatted. Does not check protocol version mismatch !"""
        if self.frame_number.bit_length() > 4 and type(self.packet_type) != PacketType:
            return False

        # Can't compute the payload of the NumPy array directly, we need its binary representation
        return Packet.compute_crc(self) == self.payload_crc

    def serialize(self) -> bytes:
        """Serialize this packet's content and returns the binary string"""
        # We concat ProtocolVer and PacketType to save some space and use only a single byte for their storage
        # Please check `comm_protocol_definition.md` for more details
        proto_ptype_channelcount = (Packet.PROTOCOL_VER << 6
                                    | self.packet_type.value << 4
                                    | self.frame_channel_count << 2)
        proto_ptype_channelcount_bytes = proto_ptype_channelcount.to_bytes(1, "big")

        # Compute payload length to find the shape of the format
        # to use with struct.pack()
        actual_payload_length = self.payload_length()
        actual_payload_length_format = f"{actual_payload_length}s"
        data = struct.pack(
            Packet.PACKING_FORMAT_START + actual_payload_length_format + Packet.PACKING_FORMAT_END,
            Packet.START_MAGIC_WORD,
            proto_ptype_channelcount_bytes,
            self.frame_number,
            *self.frame_shape[:2],
            self.payload_length(),
            self.payload.tobytes(),
            self.payload_crc.to_bytes(Packet.LEN_PAYLOAD_CRC, byteorder="little"),
            Packet.END_MAGIC_WORD
        )
        return data

    @staticmethod
    def compute_crc(packet: Packet):
        """Computes and returns the payload's CRC when converted to bytes using NumPy's tobytes() method"""
        return Packet.CRC_COMPUTER.checksum(packet.payload.tobytes())

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
    p = Packet(0xFA, PacketType.FRAME, np.array(((5, 6), (4, 3)), dtype=np.ubyte))
    s = p.serialize()
    pds = Packet.deserialize(s)
    print(pds.is_valid())
