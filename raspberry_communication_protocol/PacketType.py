from enum import Enum


class PacketType(Enum):
    """
    Represents which type of packet is being sent.

    OK: The receiver has correctly received the payload \n
    FRAME: The payloads contains an image frame \n
    HALT: One of the clients requests to end the connection \n
    REQUEST_AGAIN: Requests to send the last packet one more time, because it was damaged during transmission
    """
    OK = 0b00
    FRAME = 0b01
    HALT = 0b10
    REQUEST = 0b11
