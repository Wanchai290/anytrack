# File version v0.2 - adjusted camera settting

# Program to control camera settings, microscope stepper motors, and LED illumination from keyboard
# Camera: Pi camera HQ
# Enable the camera: Preferences --> Raspberry Pi Configuration --> Interfaces --> Camera --> Enable --> Reboot
# Increase GPU memory (Raspberry Pi 4, max. camera resolution): Preferences --> Raspberry Pi Configuration --> Performance --> GPU memory --> Change from 128 to 144 --> Reboot
# Arduino USB communication baud rate: 57600

# The code can also be used to control the camera settings of any Pi camera without having a microscope.
# The camera is by default set at high resolution
# WARNING this file code is JUST for camera for the moment

import sys
import easygui
import serial
import time
from datetime import datetime
from pynput.keyboard import Key, KeyCode, Listener
from picamera import PiCamera

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
    # camera.preview_fullscreen = False # optional
    # camera.preview_window = (0, 50, 1280, 960) #optional
    camera.start_preview()


def shortcuts():
    camera.preview_alpha = 0
    easygui.msgbox("F1: keyboard shortcuts\
                       \n----------------------------------------------------------\
                       \n+: digital zoom in, -: digital zoom out\
                       \n----------------------------------------------------------\
                       \n0: reset camera settings\
                       \n----------------------------------------------------------\
                       \nEnter: save image \
                       \n----------------------------------------------------------\
                       \nEsc: exit", "Keyboard shortcuts")
    camera.preview_alpha = 255


shortcuts()  # display the keyboard shortcuts at the beginning
camera_reset()  # start the camera preview


def on_press(key):
    global brightness, contrast, EV, saturation, zoom
    global path, filename

    # F1: keyboard shortcuts

    if key == Key.f1:
        shortcuts()

    # region CAMERA

    # Reset camera settings
    if key == KeyCode(char='0'):
        camera_reset()

    # digital zoom

    if key == KeyCode(char='+'):
        if zoom > 0.2:
            zoom = zoom - 0.1
            camera.zoom = (0, 0, zoom, zoom)
            annotate_text = "Digital zoom:" + str(round(1 / zoom, 2)) + "X"
            camera.annotate_text = annotate_text

    if key == KeyCode(char='-'):
        if zoom < 1.0:
            zoom = zoom + 0.1
            camera.zoom = (0, 0, zoom, zoom)
            annotate_text = "Digital zoom:" + str(round(1 / zoom, 2)) + "X"
            camera.annotate_text = annotate_text

    # endregion

def on_release(key):
    global path, filename

    ### Esc: exit

    if key == Key.esc:
        sys.exit()

    ### Enter: save image

    if key == Key.enter:
        camera.annotate_text = ""
        now = datetime.now()
        output = path + "/" + filename + now.strftime("%d-%m-%H%M%S.jpg")
        time.sleep(1)
        camera.capture(output, quality=100)
        camera.annotate_text = "Photo saved"


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
