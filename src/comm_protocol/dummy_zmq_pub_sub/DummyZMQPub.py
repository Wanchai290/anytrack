import os
import time
from threading import Thread

import cv2
import numpy as np
import zmq
from PIL import Image

from src.comm_protocol.Packet import Packet
from src.comm_protocol.PacketType import PacketType


class DummyZMQPub:

    def __init__(self, port: int):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind(f"tcp://*:{port}")

    def send_messages(self, packets: list[Packet]):
        print("[PUB] Waiting for subscriber")
        time.sleep(1)
        for p in packets:
            print("[PUB] Sending message")
            ser_p = p.serialize()
            self._socket.send(ser_p)
            time.sleep(0.5)

        self._context.destroy()
