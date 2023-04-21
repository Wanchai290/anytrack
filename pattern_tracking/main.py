import cv2 as cv
import numpy as np

from pattern_tracking.utils import alpha_blend, get_roi

# -- Constants
# Name of the window displayed to the user
WINDOW_NAME = 'Live template matching prototype'

# Number of pixels defining the width and height
# of the region of interest
ROI_WIDTH, ROI_HEIGHT = 50, 50

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
        roi = get_roi(live_frame, int(x-ROI_WIDTH/2), ROI_WIDTH, int(y-ROI_HEIGHT/2), ROI_HEIGHT)


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


def highlight_roi(image: cv.Mat | np.ndarray, region: np.ndarray) -> np.ndarray:
    """
    With a given image and a given region of interest, computes
    the location of the region, and applies a rectangle where the
    region of interest has been located

    The template matching method is the Normalized Cross-Correlation algorithm

    :param image: The base image, in which to find the ROI.
                  Warning: It is modified by this algorithm, to not waste memory
    :param region: The region of interest to find in the image
    :return: The base image with a rectangle applied on the matched ROI
    """
    confidence_map = cv.matchTemplate(
        image, region,
        cv.TM_CCORR_NORMED  # used by DippMotion-V program
    )

    # fetch best match possibility location
    _, _, _, top_left_max_loc = cv.minMaxLoc(confidence_map)
    bottom_right_max_loc = (top_left_max_loc[0] + region.shape[0], top_left_max_loc[1] + region.shape[1])

    # apply it on the drawing mask, which is reset right before
    global drawing_mask
    drawing_mask = np.zeros((*live_frame.shape[:2], 4), dtype=np.uint8)
    cv.rectangle(drawing_mask, top_left_max_loc, bottom_right_max_loc, (255, 255, 255, 255), 1)

    return drawing_mask


def run():
    global live_feed, live_frame
    global drawing_mask
    global roi

    # -- live display loop
    ret, live_frame = live_feed.read()
    # required to merge mask onto current frame
    live_frame = cv.cvtColor(live_frame, cv.COLOR_RGB2RGBA)
    key_pressed = 0

    while ret and live_feed.isOpened() and key_pressed != ord('q'):

        if roi is not None:
            drawing_mask = highlight_roi(live_frame, roi)
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
