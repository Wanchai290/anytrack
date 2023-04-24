import cv2 as cv
import numpy as np

from pattern_tracking.utils import alpha_blend, get_roi
from cardinal_directions import Direction

# -- Constants
# Name of the window displayed to the user
WINDOW_NAME = 'Live template matching prototype'

# Number of pixels defining the width and height
# of the region of interest
ROI_WIDTH, ROI_HEIGHT = 50, 50

# When detecting a template in the current live feed,
# if the detection is not at least above the given
# number, then we should not apply a rectangle
DETECTION_THRESHOLD = 0.9

# -- Global variables definition
# These two are used to store the cv.VideoCapture object
# and the cv.Mat object of the current frame
live_feed: cv.VideoCapture
live_frame: np.ndarray

# The additional drawing mask is overlapped onto the live video feed
# It has the same shape as the video, but with the alpha channel added
drawing_mask: np.ndarray

# The currently selected ROI that is defined
# by the user to track and display in real-time
roi: np.ndarray = None


def mouse_click_handler(event, x, y, flags, param):
    global live_frame
    global drawing_mask
    global roi
    if event == cv.EVENT_LBUTTONDOWN:
        # TODO: be able to place ROI on edges properly
        roi = get_roi(live_frame, int(x - ROI_WIDTH / 2), ROI_WIDTH, int(y - ROI_HEIGHT / 2), ROI_HEIGHT)


def setup(camera_id: int):
    global live_feed, live_frame

    live_feed = cv.VideoCapture(camera_id)

    ret, live_frame = live_feed.read()
    if not live_feed.isOpened() or not ret:
        raise IOError("Couldn't open camera feed !")

    cv.namedWindow(WINDOW_NAME)
    cv.setWindowProperty(WINDOW_NAME, cv.WND_PROP_OPENGL, 1)  # enable OpenGL
    cv.setMouseCallback(WINDOW_NAME, mouse_click_handler)

    global drawing_mask
    drawing_mask = np.zeros((*live_frame.shape[:2], 4), dtype=np.uint8)
    drawing_mask = cv.cvtColor(drawing_mask, cv.COLOR_RGB2RGBA)


def compute_cross_tracking_regions(image: cv.Mat | np.ndarray, region_xwyh: tuple[int, int, int, int], space_away: int) \
        -> dict[Direction, np.ndarray]:
    """
    With a given image, and the region of interest to find in this image,
    computes up to 4 additional regions that will serve to track the original
    given region.
    :param image: The base image
    :param region_xwyh: The top-left coordinates, width and height of the ROI in the base image
                        Order is as follows : (x, w, y, h)
    :param space_away: The number of pixels that should separate the
                       additional regions from the original one
    :return: Up to 4 regions to track, in the four cardinal directions (North, East, South, West)
    """
    compass_regions: dict[Direction, np.ndarray] = {}
    rx, rw, ry, rh = region_xwyh

    dir_region_xwyh: dict[Direction, tuple[int, int, int, int]] = {
        Direction.NORTH: (rx, rw, ry - space_away, rh),
        Direction.EAST: (rx + space_away, rw, ry, rh),
        Direction.SOUTH: (rx, rw, ry + space_away, rh),
        Direction.WEST: (rx - space_away, rw, ry, rh)
    }

    for direction, xwyh in dir_region_xwyh.items():
        try:
            compass_regions[direction] = get_roi(image, *xwyh)
        except IndexError:
            continue

    return compass_regions


def cross_template_match(image: cv.Mat | np.ndarray, cross_regions: dict[Direction, tuple[int, int, int, int]]) \
        -> np.ndarray:
    if Direction.NORTH in cross_regions.keys() and Direction.SOUTH in cross_regions.keys():
        cmap = cv.matchTemplate(image, cross_regions.get(Direction.NORTH))


def find_template_in_image(image: cv.Mat | np.ndarray, region: np.ndarray, detection_threshold: float)\
        -> tuple[tuple[int, int], tuple[int, int]]:
    """
    In a given image, computes the possible locations of the
    given region (template) to find, and returns the location
    :param image: The base image, in which to find the ROI.
    :param region: The region of interest to find in the image
    :param detection_threshold: Minimum value of the match correlation, to consider the matched region as valid
    :return: The xy location of the region in the image, or (-1, -1) if no match has been found
    """
    region_matched_location = (-1, -1)
    confidence_map = cv.matchTemplate(
        image, region,
        cv.TM_CCORR_NORMED
    )

    # fetch best match possibility location
    _, max_val, _, top_left_max_loc = cv.minMaxLoc(confidence_map)
    bottom_right_max_loc: tuple[int, int] = (top_left_max_loc[0] + region.shape[0], top_left_max_loc[1] + region.shape[1])

    if max_val >= detection_threshold:
        region_matched_location = (top_left_max_loc, bottom_right_max_loc)

    return region_matched_location


def update_drawing_mask(drawing_sheet: cv.Mat | np.ndarray, corners: tuple[tuple[int, int], tuple[int, int]]) \
        -> np.ndarray:
    """
    Resets the drawing mask, and applies a rectangle at the given xy tuple location
    :param corners: Tuple of the top-left coordinates and bottom-right
    :param drawing_sheet: The image to draw on
    :return: The modified drawing mask
    """
    # apply it on the drawing mask, which is reset right before
    drawing_sheet = np.zeros((*live_frame.shape[:2], 4), dtype=np.uint8)
    cv.rectangle(drawing_sheet, corners[0], corners[1], (255, 255, 255, 255), 1)

    return drawing_sheet


def run():
    global live_feed, live_frame
    global drawing_mask
    global roi

    ret, live_frame = live_feed.read()

    # required to merge mask onto current frame
    live_frame = cv.cvtColor(live_frame, cv.COLOR_RGB2RGBA)
    key_pressed = 0

    while ret and live_feed.isOpened() and key_pressed != ord('q'):

        if roi is not None:
            matched_region = find_template_in_image(live_frame, roi, DETECTION_THRESHOLD)
            drawing_mask = update_drawing_mask(drawing_mask, matched_region)
        frame = alpha_blend(live_frame, drawing_mask)

        cv.imshow(WINDOW_NAME, frame)
        key_pressed = cv.waitKey(1)
        ret, live_frame = live_feed.read()
        live_frame = cv.cvtColor(live_frame, cv.COLOR_RGB2RGBA)

    live_feed.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    setup(0)
    run()
