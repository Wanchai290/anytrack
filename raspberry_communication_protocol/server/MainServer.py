import numpy as np
import cv2 as cv
from queue import Queue
from threading import Thread, Event

from PIL import Image

from raspberry_communication_protocol.FrameTCPClient import FrameTCPClient
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
    client = FrameTCPClient("localhost", Main.SERVER_PORT, halt, Event())
    client.run_forever()
    _, received_img = client.received_frames_queue.get()
    halt.set()
    m.halt()
    cv.imshow("nice cat", received_img)
    cv.waitKey(0)  # press a key when window opens so that the code below gets run anyway
    cv.destroyAllWindows()
    exit(0)
