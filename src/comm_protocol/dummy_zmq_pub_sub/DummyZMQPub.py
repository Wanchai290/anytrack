import os
import time
from threading import Thread

import cv2
import numpy as np
import zmq

from src.comm_protocol.Packet import Packet


class DummyZMQPub:

    def __init__(self, port: int):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind(f"tcp://*:{port}")

    def send_messages(self, packets: list[Packet], time_fmt: str):
        """
        Send the packets given over its ZMQ socket
        Params:
            packets     -- Packets to send, in the format of `Packet.py`
            time_fmt    -- String format to print the time in
        """
        print(f"[PUB - " + eval(f"f'{time_fmt}'") + "] Waiting one second for subscribers to prepare...")
        time.sleep(1)
        for p in packets:
            print(f"[PUB - " + eval(f"f'{time_fmt}'") + "] Sending message")
            ser_p = p.serialize()
            self._socket.send(ser_p)
            time.sleep(0.1)

        self._context.destroy()
