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
        - self._frame_id: 4 bits length, the ID of the frame
        - self._packet_type: 2 bits length, type of packet sent
        - self._payload: Arbitrary length, the NumPy array containing the frame
        - self._payload_crc: CRC checksum of the payload

        dev note: maybe I could compute the CRC against the whole packet, but only the frame is used most of the time
    """

    PROTOCOL_VER = 0x01
    # note: there was no proper choice when choosing the polynomial here, it's just to have a CRC to check for
    CRC_COMPUTER = crc.Calculator(crc.Crc16.CCITT.value)

    def __init__(self, frame_id: int, packet_type: PacketType, payload: np.ndarray):
        self._frame_id = frame_id
        self._packet_type = packet_type
        self._payload = payload
        # CRC is computed over packet's unique data
        self._payload_crc = Packet.compute_crc(self)

    def is_valid(self):
        """Returns True if the packet is correctly formatted. Does not check protocol version mismatch !"""
        if self._frame_id.bit_length() > 4 and type(self._packet_type) != PacketType:
            return False

        # Can't compute the payload of the NumPy array directly, we need its binary representation
        return Packet.compute_crc(self) == self._payload_crc

    def serialize(self) -> bytes:
        """Serialize this packet's content and returns the binary string"""
        raw = io.BytesIO()
        # we send the whole packet's data, including the CRC of the data sent
        data = np.array(
            (
                Packet.PROTOCOL_VER,
                self._frame_id,
                self._packet_type,
                self._payload,
                self._payload_crc
            ),
            dtype=object)
        np.save(raw, data)

        raw.seek(0)
        return raw.getvalue()

    @staticmethod
    def compute_crc(packet: Packet):
        """Computes and returns the payload's CRC when saved using np.save()"""
        f = io.BytesIO()
        np.save(
            f,
            np.array((
                Packet.PROTOCOL_VER,
                packet._frame_id,
                packet._packet_type,
                packet._payload
            ), dtype=object)
        )
        f.seek(0)
        return Packet.CRC_COMPUTER.checksum(f.getvalue())

    @staticmethod
    def deserialize(serialized_packet: bytes, raw: bool = False) -> Any | Packet:
        """Deserializes a packet, and returns either the raw data, or a Packet object"""
        f = io.BytesIO(serialized_packet)
        raw_data = np.load(f, allow_pickle=True)
        if raw:
            return raw_data
        else:
            return Packet(*raw_data[1:4])


if __name__ == '__main__':
    p = Packet(0x01, PacketType.FRAME, np.array((5, 6)))
    s = p.serialize()
    pds = Packet.deserialize(s, False)
    print(pds.is_valid())
