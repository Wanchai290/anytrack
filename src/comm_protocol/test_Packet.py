import numpy as np

from unittest import TestCase

from src.comm_protocol.Packet import Packet


class TestPacket(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self._p_data = (1, np.zeros((2, 2, 3), dtype=np.uint8))
        self._p = Packet(*self._p_data)

    def test_no_change_after_transfer(self):
        p_ser = self._p.serialize()
        p_deser = Packet.deserialize(p_ser)
        self.assertEqual(self._p, p_deser)

    def test_eq_override(self):
        p_copy = Packet(*self._p_data)
        self.assertEqual(self._p, p_copy)

    def test_types_valid_after_deser(self):
        p_deser = Packet.deserialize(self._p.serialize())
        self.assertEqual(type(p_deser.frame_number), type(self._p.frame_number))
        self.assertEqual(type(p_deser.frame_shape), type(self._p.frame_shape))
        self.assertEqual(type(p_deser.frame_channel_count), type(self._p.frame_channel_count))
        self.assertEqual(type(p_deser.payload), type(self._p.payload))

    def test_serialize(self):
        p = Packet(0xFA, np.zeros((2, 2, 3), dtype=np.uint8))
        p_ser = p.serialize()
        self.assertEqual(p_ser, b'INU\xcc\xfa\x00\x00\x00\x02\x00\x02\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00NEKO')
        self.assertEqual(Packet.deserialize(p_ser), p)

        p = Packet(0xFA, np.full((2, 2, 3), 4, dtype=np.uint8))
        p_ser = p.serialize()

        self.assertEqual(p_ser, b'INU\xcc\xfa\x00\x00\x00\x02\x00\x02\x00\x0c\x00\x00\x00\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04NEKO')
        self.assertEqual(Packet.deserialize(p_ser), p)

    def test_serialize_twodim_arr(self):
        p = Packet(1, np.array(((2, 3), (4, 5)), dtype=int))
        p_ser = p.serialize()
        p_deser = Packet.deserialize(p_ser)
        self.assertEqual(p, p_deser)
