from __future__ import annotations

import dataclasses
import typing
from enum import Enum
from typing import Callable

import numpy as np


# Dev note: replacing the namedtuple with a dataclass made it possible to refactor code in PyCharm
# I'm sacrificing a little bit of speed for better coding experience
@dataclasses.dataclass
class PacketDataTypeValue:
    binary_form: int
    type_: type


class PacketDataType(Enum):
    """
    Describes the allowed data types of the NumPy array that represents
    the frame to send with this protocol. Stored on 2 bits (this value is written in `Packet.py`)

    Note that the type noted next to the binary form is not numpy.dtype,
    but instead the type of the dtype attribute (so in the end, a `type` object)

    Quick example : \n
    `> a = np.array((1,2))`  \n
    `> a.dtype` \n
    `dtype('int32')` \n
    `> a.dtype.type` \n
    `<class 'numpy.int32'>`
    ```
    """
    U8_INT = PacketDataTypeValue(0b00, np.ubyte)
    U16_INT = PacketDataTypeValue(0b01, np.ushort)
    U32_INT = PacketDataTypeValue(0b10, np.int32)
    U64_INT = PacketDataTypeValue(0b11, np.int64)

    @classmethod
    def from_dtype(cls, dtype: np.dtype) -> int:
        """
        Using a NumPy data type, find the number that represents this data type
        :param dtype: NumPy dtype object
        :return: The binary form representing this data type
        :raise ValueError if this data type is not supported
        """
        type_ = dtype.type
        test = lambda val: type_ == val.type_
        pdtype_value = PacketDataType.find(test)

        if pdtype_value is None:
            raise ValueError("This NumPy data type is not supported by this communication protocol. "
                             "Please check this class' definition for the allowed types")

        return pdtype_value.binary_form

    @classmethod
    def from_bin_form(cls, bin_form: int):
        """
        Using the binary representation as an int, find the corresponding type object
        :param bin_form: First value in the values of the enum, the binary representation of a data type in the protocol
        :return: The type object represented by this binary form
        :raise ValueError if this number does not correspond to any data type supported
        """
        test = lambda val: bin_form == val.binary_form
        pdtype_value = PacketDataType.find(test)

        if pdtype_value is None:
            raise ValueError("The number provided is not a valid representation"
                             "of any type supported by this protocol.")

        return pdtype_value.type_

    @classmethod
    def find(cls, test: Callable[[PacketDataTypeValue], bool]) -> typing.Union[PacketDataTypeValue, None]:
        finished = False
        result: typing.Union[type, None] = None
        generator = enumerate(PacketDataType)

        v = next(generator)
        while not finished:
            if test(v[1].value):
                result = v[1].value
            v = next(generator, None)
            finished = result is not None or v is None

        return result


if __name__ == '__main__':
    a = np.array((1, 2), dtype=int)
    print(PacketDataType.from_dtype(a.dtype))
