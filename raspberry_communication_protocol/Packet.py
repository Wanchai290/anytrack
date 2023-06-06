import io
import pickle

import numpy as np

from raspberry_communication_protocol.PacketType import PacketType


class Packet:

    PROTOCOL_VER = 0x01

    def __init__(self, packet_number: hex, packet_type: PacketType):
        self._packet_number = packet_number
        self._packet_type = packet_type
        self._payload: np.ndarray = np.array((5, 5))

    def serialize(self) -> bytes:
        raw = io.BytesIO()
        data = np.array((
            self._packet_number,
            self._packet_type
        ))
        np.save(raw, data)
        raw.seek(0)
        return raw.getvalue()

    @staticmethod
    def deserialize(serialized_packet: bytes):
        f = io.BytesIO(serialized_packet)
        packet = np.load(f, allow_pickle=True)
        return packet


if __name__ == '__main__':
    p = Packet(0x11, PacketType.BUFFER_START)
    s = p.serialize()
    pds = Packet.deserialize(s)
    print(pds[0])