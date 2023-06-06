from enum import Enum


class PacketType(Enum):
    ACCEPT = 0b00
    BUFFER_START = 0b01
    BUFFER_END = 0b10
    REQUEST_AGAIN = 0b11
