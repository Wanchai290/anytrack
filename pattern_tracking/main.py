import cv2 as cv
import numpy as np

from pattern_tracking.utils import alpha_blend, get_roi, middle_of
from cardinal_directions import Direction

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
poi: np.ndarray = None
poi_xwyh: tuple[int, int, int, int] = (-1, -1, -1, -1)

# Remembers the region in which to find a specific ROI
# This is to avoid searching in the whole image for the template
region_limit_xwyh = (0, 0, 0, 0)
region_limit_start, region_limit_end = (0, 0), (0, 0)

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
        poi_xwyh = (int(x - POI_WIDTH / 2), POI_WIDTH, int(y - POI_HEIGHT / 2), POI_HEIGHT)
        poi = get_roi(live_frame, *poi_xwyh)

    elif event == cv.EVENT_RBUTTONDOWN:
        is_drawing = True
        region_limit_start = (x, y)
        region_limit_end = (x, y)

    elif event == cv.EVENT_MOUSEMOVE and is_drawing:
        region_limit_end = (x, y)
    elif event == cv.EVENT_RBUTTONUP:
        is_drawing = False
        rx, rw, ry, rh = \
            min(region_limit_start[0], region_limit_end[0]), \
            abs(region_limit_end[0] - region_limit_start[0]), \
            min(region_limit_start[1], region_limit_end[1]), \
            abs(region_limit_end[1] - region_limit_start[1])

        region_limit_xwyh = rx, rw, ry, rh


def setup(camera_id: int):
    global live_feed, live_frame

    live_feed = cv.VideoCapture(camera_id)

    ret, live_frame = live_feed.read()
    if not live_feed.isOpened() or not ret:
        raise IOError("Couldn't open camera feed !")

    cv.namedWindow(WINDOW_NAME, cv.WINDOW_GUI_NORMAL)  # WINDOW_GUI_NORMAL to disable default right-click dropdown menus
    cv.setWindowProperty(WINDOW_NAME, cv.WND_PROP_OPENGL, 1)  # enable OpenGL
    cv.setMouseCallback(WINDOW_NAME, mouse_click_handler)


def find_template_in_image(image: cv.Mat | np.ndarray, roi: np.ndarray, detection_threshold: float) \
        -> tuple[tuple[int, int], tuple[int, int]]:
    """
    In a given image, computes the possible locations of the
    given region (template) to find, and returns the location
    :param image: The base image, in which to find the ROI.
    :param roi: The region of interest to find in the image
    :param detection_threshold: Minimum value of the match correlation, to consider the matched region as valid
    :return: The xy location of the region in the image, or (-1, -1) if no match has been found
    """
    region_matched_location = (-1, -1)
    confidence_map = cv.matchTemplate(
        image, roi,
        cv.TM_CCORR_NORMED
    )

    # fetch best match possibility location
    _, max_val, _, top_left_max_loc = cv.minMaxLoc(confidence_map)
    bottom_right_max_loc: tuple[int, int] = (
        top_left_max_loc[0] + roi.shape[0], top_left_max_loc[1] + roi.shape[1])

    if max_val >= detection_threshold:
        region_matched_location = (top_left_max_loc, bottom_right_max_loc)

    return region_matched_location


def run():
    global live_feed, live_frame
    global poi, poi_xwyh
    global region_limit_xwyh, region_limit_start, region_limit_end

    ret, live_frame = live_feed.read()

    key_pressed = 0

    while ret and live_feed.isOpened() and key_pressed != ord('q'):

        frame = live_frame  # todo: is diz a copy ?
        # draw current region bounds selected, ie where to find the image to track
        region_limit: np.ndarray = None
        if region_limit_xwyh != (0, 0, 0, 0):
            cv.rectangle(frame, region_limit_start, region_limit_end, (0, 255, 0, 255), 2)
            region_limit = get_roi(live_frame, *region_limit_xwyh)

        # draw currently selected poi, ie the part of the image to track
        if poi is not None:
            offset: tuple[int, int] = (0, 0)

            if region_limit is None:
                matched_region = find_template_in_image(live_frame, poi, DETECTION_THRESHOLD)

            else:
                matched_region = find_template_in_image(region_limit, poi, DETECTION_THRESHOLD)
                offset = region_limit_start

            # offset the found region
            if matched_region != (-1, -1):
                matched_region = (
                    (
                        matched_region[0][0] + offset[0],
                        matched_region[0][1] + offset[1]
                    ),
                    (
                        matched_region[1][0] + offset[0],
                        matched_region[1][1] + offset[1]
                    )
                )

                cv.rectangle(frame, *matched_region, (255, 255, 255, 255), 2)

        cv.imshow(WINDOW_NAME, frame)
        key_pressed = cv.waitKey(1)
        ret, live_frame = live_feed.read()
        live_frame = cv.cvtColor(live_frame, cv.COLOR_RGB2RGBA)

    live_feed.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    setup(0)
    # setup("./test_assets/ムービー_49.avi")
    run()
