# Custom software that integrates with Wanchai's Live Tracking Software
# It is a modified version of Alex DUFOUR's software to visualize the content of the integrated camera in the RaspberryPI
# Below is the original documentation of Alex's software

# ----------------------------------------------------

# Program to control camera settings, microscope stepper motors, and LED illumination from keyboard
# Camera: Pi camera HQ
# Enable the camera: Preferences --> Raspberry Pi Configuration --> Interfaces --> Camera --> Enable --> Reboot
# Increase GPU memory (Raspberry Pi 4, max. camera resolution): Preferences --> Raspberry Pi Configuration --> Performance --> GPU memory --> Change from 128 to 144 --> Reboot
# Arduino USB communication baud rate: 57600

# The code can also be used to control the camera settings of any Pi camera without having a microscope.
# The camera is by default set at high resolution
# WARNING this file code is JUST for camera for the moment

from queue import Queue
from threading import Thread, Event

import numpy as np
from picamera import PiCamera

from comm_protocol.server.FrameTCPServer import FrameTCPServer
from comm_protocol.server.FrameTCPServerRequestHandler import FrameTCPServerRequestHandler

# Camera
camera = PiCamera()
brightness = 50  # start-up brightness
contrast = 0  # start-up contrast
EV = 0  # start-up exposure compensation
saturation = 0  # start-up saturation

zoom = 1.0  # start-up digital zoom factor

filename = ""  # default filename prefix
path = "/home/PIctures"  # default path


def camera_reset():
    global brightness, contrast, EV, saturation
    brightness = 50
    contrast = 0
    
    EV = 0
    saturation = 0
    camera.brightness = brightness
    camera.contrast = contrast
    camera.exposure_compensation = EV
    camera.saturation = saturation
    camera.sensor_mode = 2  # full field of view
    camera.resolution = (3888, 2592)  # 10MP
    camera.rotation = 180
    camera.annotate_text_size = 100
    camera.annotate_text = ""
    camera.iso = 0
    camera.shutter_speed = 0
    camera.framerate = 30
    camera.exposure_mode = 'auto'
    camera.awb_mode = 'auto'


def main():
    camera_reset()  # start the camera preview
    np_shape = (*camera.resolution[::-1], 3)
    frames_queue: Queue[tuple[int, np.ndarray]] = Queue()
    frame_num = 0
    ip_address = input("IP address of the RaspberryPi on interface eth0 ?")
    # Create an Event object for halting the server
    halt_event = Event()
    
    # Create an instance of FrameTCPServer with all required arguments
    server = FrameTCPServer((ip_address, FrameTCPServer.DEFAULT_PORT), FrameTCPServerRequestHandler, frames_queue, halt_event)

    # start the server on a separate thread
    thread = Thread(target=server.serve_forever)
    thread.start()

    # keep capturing data into the output
    while True:
        img_arr = np.empty(np_shape, dtype=np.uint8)
        camera.capture(img_arr, 'rgb')
        frames_queue.put((frame_num, img_arr))


if __name__ == '__main__':
    main()
