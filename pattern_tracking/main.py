import cv2 as cv
import numpy as np

from pattern_tracking.utils import get_roi, normalize_region, find_template_in_image

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
# These two are used to store the cv.VideoCapture object
# and the cv.Mat object of the current frame
live_feed: cv.VideoCapture
live_frame: np.ndarray

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


def setup(camera_id: int):
    global live_feed, live_frame

    live_feed = cv.VideoCapture(camera_id)

    ret, live_frame = live_feed.read()
    if not live_feed.isOpened() or not ret:
        raise IOError("Couldn't open camera feed !")

    cv.namedWindow(WINDOW_NAME, cv.WINDOW_GUI_NORMAL)  # WINDOW_GUI_NORMAL to disable default right-click dropdown menus
    cv.setWindowProperty(WINDOW_NAME, cv.WND_PROP_OPENGL, 1)  # enable OpenGL
    cv.setMouseCallback(WINDOW_NAME, mouse_click_handler)


def run():
    global live_feed, live_frame
    global poi, poi_xwyh
    global region_limit_xwyh, region_limit_start, region_limit_end

    ret, live_frame = live_feed.read()

    key_pressed = 0

    while ret and live_feed.isOpened() and key_pressed != ord('q'):

        frame = live_frame  # todo: is diz a copy ?
        # draw current region bounds selected, ie where to find the image to track
        region_limit: np.ndarray = np.array([-1])
        if region_limit_xwyh[region_limit_xwyh == 0].all():
            cv.rectangle(frame, region_limit_start, region_limit_end, (0, 255, 0, 255), 2)
            region_limit = get_roi(live_frame, *region_limit_xwyh)

        # draw currently selected poi, ie the part of the image to track
        if not (poi == -1).any() and not is_drawing:
            offset: np.ndarray = np.array([0, 0])

            if (region_limit == -1).any():
                matched_region = find_template_in_image(live_frame, poi, DETECTION_THRESHOLD)

            else:
                matched_region = find_template_in_image(region_limit, poi, DETECTION_THRESHOLD)
                offset = region_limit_start

            # offset the found region & display it
            if not (matched_region == -1).any():
                matched_region += offset
                cv.rectangle(frame, *matched_region, (255, 255, 255, 255), 2)

        cv.imshow(WINDOW_NAME, frame)
        key_pressed = cv.waitKey(1)
        ret, live_frame = live_feed.read()

    live_feed.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    setup(0)
    # setup("./test_assets/ムービー_49.avi")
    run()
