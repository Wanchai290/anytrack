import socket
import time

import numpy as np
import cv2 as cv
from queue import Queue
from threading import Thread, Lock, Event

from PIL import Image

from raspberry_communication_protocol.FrameTCPClient import FrameTCPClient
from raspberry_communication_protocol.Packet import Packet
from raspberry_communication_protocol.PacketHandler import PacketHandler
from raspberry_communication_protocol.PacketType import PacketType
from raspberry_communication_protocol.server.FrameTCPServer import FrameTCPServer
from raspberry_communication_protocol.server.FrameTCPServerRequestHandler import FrameTCPServerRequestHandler


class Main:

    # SERVER_PORT = 47827
    SERVER_PORT = 2556

    def __init__(self, host: str, port: int):
        self.frames_queue = Queue()
        self.conn_info = (host, port)
        self.server = FrameTCPServer(self.frames_queue, self.conn_info, FrameTCPServerRequestHandler)

    def serve(self):
        self.server.serve_forever()

    def halt(self):
        self.server.shutdown()


if __name__ == "__main__":
    m = Main("localhost", Main.SERVER_PORT)
    img = Image.open("cat_look.jpeg")
    frame = np.asarray(img, dtype=np.uint8)
    m.frames_queue.put((0, frame))
    t = Thread(target=m.serve)
    t.start()

    halt = Event()
    client = FrameTCPClient("localhost", Main.SERVER_PORT, halt)
    client.run_forever()
    _, received_img = client.received_frames_queue.get()
    cv.imshow("nice cat", received_img)
    cv.waitKey(0)
    m.halt()

    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #     sock.connect(("localhost", Main.SERVER_PORT))
    #     p = Packet.placeholder()
    #     p.packet_type = PacketType.OK
    #     sock.send(p.serialize())
    #
    #     response = PacketHandler.read_start_word(sock)
    #     if response is not None:
    #         response += PacketHandler.read_until_end_word(sock, time.time(), 999)
    #
    #     packet_response = Packet.deserialize(response)
    #     print(packet_response.packet_type)
    #     print(packet_response.payload.shape)
    #     print(cv.imshow("nice cat", packet_response.payload))
    #     cv.waitKey(0)
    #     m.halt()
