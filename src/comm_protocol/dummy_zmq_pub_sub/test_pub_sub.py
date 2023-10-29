import os
from threading import Thread

import cv2
import numpy as np
import zmq
from PIL import Image

from src.comm_protocol.Packet import Packet
from src.comm_protocol.PacketType import PacketType
from src.comm_protocol.dummy_zmq_pub_sub.DummyZMQPub import DummyZMQPub
from src.comm_protocol.dummy_zmq_pub_sub.DummyZMQSub import DummyZMQSub

if __name__ == '__main__':
    port = 61089
    zmq_sub = DummyZMQSub(port)
    zmq_pub = DummyZMQPub(port)

    # load dummy frames
    dir_path = "assets/dummy_zmq_pub_frames/"
    frames = []
    directory = os.listdir(os.path.join(os.getcwd(), dir_path))
    for f_name in sorted(directory):
        frames.append(
            np.array(
                Image.open(os.path.join(dir_path, f_name))
            )
        )

    received_frames = {}

    th_sub = Thread(
        target=zmq_sub.recv_messages,
        args=(len(frames), received_frames,)
    )
    th_sub.start()

    th_pub = Thread(
        target=zmq_pub.send_messages,
        args=([Packet(i, PacketType.FRAME, frames[i]) for i in range(len(frames))],)
    )
    th_pub.run()
    th_sub.join()

    print(f"Obtained frames : {len(received_frames)}")

    for packet in received_frames.values():
        cv2.imshow("Frames received", packet.payload[:, :, ::-1])
        cv2.waitKey(50)
