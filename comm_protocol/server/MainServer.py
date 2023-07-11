import numpy as np
import cv2 as cv
from queue import Queue
from threading import Thread, Event

from PIL import Image

from comm_protocol.FrameTCPClient import FrameTCPClient
from comm_protocol.server.FrameTCPServer import FrameTCPServer
from comm_protocol.server.FrameTCPServerRequestHandler import FrameTCPServerRequestHandler


class Main:

    def __init__(self, host: str, port: int, halt_event: Event):
        self.frames_queue = Queue()
        self.conn_info = (host, port)
        self.server = FrameTCPServer(self.frames_queue, halt_event, self.conn_info, FrameTCPServerRequestHandler)

    def serve(self):
        self.server.serve_forever()

    def halt(self):
        self.server.shutdown()


if __name__ == "__main__":
    halt = Event()
    m = Main("localhost", FrameTCPServer.DEFAULT_PORT, halt)
    img = Image.open("cat_look.jpeg")
    frame = np.asarray(img, dtype=np.uint8)
    m.frames_queue.put((0, frame))
    m.frames_queue.put((1, frame.copy()))
    t = Thread(target=m.serve)
    t.start()

    client = FrameTCPClient("localhost", FrameTCPServer.DEFAULT_PORT, halt, Event())
    client.run_forever()
    _ = client.received_frames_queue.get()
    _, received_img = client.received_frames_queue.get()
    halt.set()
    m.halt()
    cv.imshow("nice cat", received_img)
    cv.waitKey(0)  # press a key when window opens so that the code below gets run anyway
    cv.destroyAllWindows()
    exit(0)
