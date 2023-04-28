from queue import Queue
from threading import Thread, Event

import cv2 as cv
import numpy as np

from pattern_tracking.utils import get_roi, normalize_region, find_template_in_image, video_reader

# -- Constants
# Name of the window displayed to the user
WINDOW_NAME = 'Live template matching prototype'

# Number of pixels defining the width and height
# of the region of interest
POI_WIDTH, POI_HEIGHT = 50, 50

# When detecting a template in the current live feed,
# if the detection is not at least above the given
# number, then we should not apply a rectangle
DETECTION_THRESHOLD = 0.99

# -- Global variables definition
# For the video feed and the background video reader thread
# All other tasks rely on the video reader
live_feed: cv.VideoCapture
live_frame: np.ndarray
frames_queue: Queue[tuple[int, cv.Mat]]
th_vid_reader: Thread
halt_work: Event


# The currently selected POI that is defined
# by the user to track and display in real-time
poi: np.ndarray = np.array([-1])
poi_xwyh: np.ndarray = np.array([-1, -1, -1, -1], dtype=int)

# Remembers the region in which to find a specific ROI&
# This is to avoid searching in the whole image for the template
region_limit_xwyh: np.ndarray = np.array([0, 0, 0, 0], dtype=int)
region_limit_start: np.ndarray = np.array([0, 0])
region_limit_end: np.ndarray = np.array([0, 0])

# Used to handle drawing rectangles on the screen,
# and to highlight the specified ROI
is_drawing: bool = False


def mouse_click_handler(event, x, y, flags, param):
    global live_frame
    global poi, poi_xwyh
    global region_limit_xwyh, region_limit_start, region_limit_end
    global is_drawing

    if event == cv.EVENT_LBUTTONDOWN:
        # TODO: be able to place POI on edges properly
        poi_xwyh[:] = (int(x - POI_WIDTH / 2), POI_WIDTH, int(y - POI_HEIGHT / 2), POI_HEIGHT)
        poi = get_roi(live_frame, *poi_xwyh)

    elif event == cv.EVENT_RBUTTONDOWN:
        is_drawing = True
        region_limit_start[:] = (x, y)
        region_limit_end[:] = (x, y)

    elif event == cv.EVENT_MOUSEMOVE and is_drawing:
        region_limit_end[:] = (x, y)

    elif event == cv.EVENT_RBUTTONUP:
        is_drawing = False

        # normalize selected region
        region_limit_start, region_limit_end = normalize_region(region_limit_start, region_limit_end)

        # compute width and height
        rx, ry = region_limit_start
        rw, rh = region_limit_end[0] - region_limit_start[0], \
            region_limit_end[1] - region_limit_start[1]

        region_limit_xwyh = np.array([rx, rw, ry, rh])


def setup(camera_id: int, max_frames: int = 300):
    global live_feed, live_frame, frames_queue, th_vid_reader, halt_work

    frames_queue = Queue(max_frames)
    halt_work = Event()

    live_feed = cv.VideoCapture(camera_id)
    th_vid_reader = Thread(target=video_reader, args=(live_feed, frames_queue, halt_work))

    ret, live_frame = live_feed.read()
    if not live_feed.isOpened() or not ret:
        raise IOError("Couldn't open camera feed !")

    cv.namedWindow(WINDOW_NAME, cv.WINDOW_GUI_NORMAL)  # WINDOW_GUI_NORMAL to disable default right-click dropdown menus
    cv.setWindowProperty(WINDOW_NAME, cv.WND_PROP_OPENGL, 1)  # enable OpenGL
    cv.setMouseCallback(WINDOW_NAME, mouse_click_handler)


def run():
    global live_feed, live_frame, th_vid_reader, halt_work
    global poi, poi_xwyh
    global region_limit_xwyh, region_limit_start, region_limit_end

    th_vid_reader.start()
    _, live_frame = frames_queue.get()
    key_pressed = 0

    while not halt_work.is_set() and key_pressed != ord('q'):

        frame = live_frame  # todo: is diz a copy ?
        # draw current region bounds selected, ie where to find the image to track
        region_limit: np.ndarray = np.array([-1])
        if not (region_limit_xwyh == 0).all():
            cv.rectangle(frame, region_limit_start, region_limit_end, (0, 255, 0, 255), 2)
            region_limit = get_roi(live_frame, *region_limit_xwyh)

        # change whether we find the POI in a region, or in the whole frame
        if (region_limit == -1).any():
            roi = live_frame
            offset: np.ndarray = np.array([0, 0])
        else:
            roi = region_limit
            offset: np.ndarray = region_limit_start

        # draw currently selected poi, ie the part of the image to track
        if not (poi == -1).any() and not is_drawing \
                and (np.array(roi.shape) >= np.array(poi.shape)).all():

            poi_matched_region = find_template_in_image(roi, poi, DETECTION_THRESHOLD)

            # offset the found region & display it
            if not (poi_matched_region == -1).any():
                poi_matched_region += offset
                cv.rectangle(frame, *poi_matched_region, (255, 255, 255, 255), 2)

        cv.imshow(WINDOW_NAME, frame)
        key_pressed = cv.waitKey(1)
        _, live_frame = frames_queue.get()

    halt_work.set()
    th_vid_reader.join()

    live_feed.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    setup(0)
    # setup("./test_assets/ムービー_49.avi")
    run()
