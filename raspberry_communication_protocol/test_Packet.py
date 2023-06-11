import numpy as np

from unittest import TestCase

from raspberry_communication_protocol.Packet import Packet
from raspberry_communication_protocol.PacketType import PacketType


class Test(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self._p_data = (1, PacketType.OK, np.array((5, 5)))
        self._p = Packet(*self._p_data)

    def test_no_change_after_transfer(self):
        p_ser = self._p.serialize()
        p_deser = Packet.deserialize(p_ser)
        self.assertEquals(self._p, p_deser)

    def test_valid_after_serialize_deserialize(self):
        p_ser = self._p.serialize()
        p_deser = Packet.deserialize(p_ser)
        self.assertTrue(p_deser)

    def test_eq_override(self):
        p_copy = Packet(*self._p_data)
        self.assertEquals(self._p, p_copy)

    def test_invalid_if_crc_changed(self):
        p_ser = self._p.serialize()
        p_deser = Packet.deserialize(p_ser)
        p_deser.payload_crc = 0
        self.assertFalse()
