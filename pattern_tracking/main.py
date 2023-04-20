import cv2 as cv
import numpy as np

from pattern_tracking.utils import alpha_blend

WINDOW_NAME = 'window'

# -- Global variables definition

# These two are used to store the cv.VideoCapture object
# and the cv.Mat object of the current frame
global live_feed, live_frame

# The additional drawing mask is overlapped onto the live video feed
# It has the same shape as the video, but with the alpha channel added
global drawing_mask


def mouse_click_handler(event, x, y, flags, param):
    global live_frame
    global drawing_mask
    if event == cv.EVENT_LBUTTONDOWN:
        cv.rectangle(
            drawing_mask,
            (x-10, y-10), (x+10, y+10),
            (255, 255, 255, 255),
            10
        )


def setup(camera_id: int):
    global live_feed, live_frame

    live_feed = cv.VideoCapture(camera_id)

    ret, live_frame = live_feed.read()
    if not live_feed.isOpened() or not ret:
        raise IOError("Couldn't open camera feed !")

    cv.namedWindow(WINDOW_NAME)
    # enable OpenGL
    cv.setWindowProperty(WINDOW_NAME, cv.WND_PROP_OPENGL, 1)
    cv.setMouseCallback(WINDOW_NAME, mouse_click_handler)

    global drawing_mask
    drawing_shape = live_frame.shape[:2]
    drawing_mask = np.zeros((*drawing_shape, 4), dtype=np.uint8)
    drawing_mask = cv.cvtColor(drawing_mask, cv.COLOR_RGB2RGBA)


def run():
    global live_feed, live_frame
    global drawing_mask

    # -- live display loop
    ret, live_frame = live_feed.read()
    # required to merge mask onto current frame
    live_frame = cv.cvtColor(live_frame, cv.COLOR_RGB2RGBA)
    key_pressed = 0

    while ret and live_feed.isOpened() and key_pressed != ord('q'):
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
