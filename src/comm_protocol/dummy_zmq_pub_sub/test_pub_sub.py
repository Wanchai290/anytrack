import argparse
import os
from threading import Thread

import cv2
import numpy as np
from PIL import Image

from src.comm_protocol.Packet import Packet
from src.comm_protocol.dummy_zmq_pub_sub.DummyZMQPub import DummyZMQPub
from src.comm_protocol.dummy_zmq_pub_sub.DummyZMQSub import DummyZMQSub

if __name__ == '__main__':
    # add args
    parser = argparse.ArgumentParser(
        prog="test_pub_sub.py",
        description="By default, performs a communication test by launching a publisher and a subscriber on 127.0.0.1 "
                    "(default port is 61089). Sends a message every second.",
        epilog="You can test the pub/sub mechanism, or only launch either the publisher itself using the options"
    )

    parser.add_argument('--pub',
                        action='store_true',
                        help='Only launch on 127.0.0.1 (useful for main software test)')

    parser.add_argument('-p', '--port',
                        action='store',
                        type=int,
                        default=61089,
                        help='Specify on which port the program will work')

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
    time_format = "{time.time()%1000:.5f}"  # nasty way of specifying a time printing format

    # handle user args
    args = parser.parse_args()
    port = args.port
    normal_launch = args.pub is False

    # setup subscriber if tasked
    if normal_launch:
        zmq_sub = DummyZMQSub(port)
        th_sub = Thread(
            target=zmq_sub.recv_messages,
            args=(len(frames), received_frames, time_format,)
        )
        th_sub.start()

    # setup the publisher
    zmq_pub = DummyZMQPub(port)
    th_pub = Thread(
        target=zmq_pub.send_messages,
        args=([Packet(i, frames[i]) for i in range(len(frames))], time_format)
    )
    th_pub.run()

    if normal_launch:
        # your IDE might tell you this can be undefined, but it will never be
        # unless a random byte shifts in memory
        th_sub.join()

        print(f"Obtained frames : {len(received_frames)}")

        for packet in received_frames.values():
            cv2.imshow("Frames received", packet.payload[:, :, ::-1])  # swap BGR to RGB
            cv2.waitKey(150)
