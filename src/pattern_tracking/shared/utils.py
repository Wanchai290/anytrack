import cv2 as cv
import numpy as np
from PySide6.QtGui import QImage, QPixmap

from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest


def get_roi(image: np.ndarray, x: int, w: int, y: int, h: int) -> np.ndarray:
    """
    Selects and returns a specific ROI (Region Of Interest) from a given
    image. The top-left corner of the ROI should be specified by parameters
    x and y.
    Note that the returned ROI will be selected with the lower and upper bounds
    included (thus, between x and x+w+1 for the x coordinates)

    :param image: The image to extract the ROI from
    :param x: X coordinate of the top-left corner of the ROI
    :param w: Width of the ROI, starting from the top-left corner
    :param y: Y coordinate of the top-left corner of the ROI
    :param h: Height of the ROI, starting from the top-left corner
    :return: A copy of the image, cropped to be the ROI
    """
    x_edge = x + w
    y_edge = y + h
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x_edge > image.shape[1]:
        x_edge = image.shape[1]
    if y_edge > image.shape[0]:
        y_edge = image.shape[0]

    return image[y: y_edge, x: x_edge]


def middle_of(p1: np.ndarray | tuple[int, int], p2: np.ndarray | tuple[int, int]) \
        -> np.ndarray:
    return np.array((int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2)))


def normalize_region(pt1: np.ndarray | tuple[int, int], pt2: np.ndarray | tuple[int, int]) -> np.ndarray:
    """
    Creates a valid region by computing the minimum and maximum
    of each x and y coordinate in each point.

    Will consider that pt1 and pt2 are of length 2. No check is done in the function

    This is mainly used to get valid region coordinates
    when it is selected by the user (since the start and end point can be anywhere)

    :param pt1: Tuple of x,y coordinates
    :param pt2: Tuple of x,y coordinates
    :return: Two points, where the first point is the most top-left location,
             and the other point is the most top-right location
    """
    # TODO: use fancy math matrix instead of boring assignment
    x_coords = (pt1[0], pt2[0])
    y_coords = (pt1[1], pt2[1])

    min_x_index = min(range(len(x_coords)), key=x_coords.__getitem__)
    min_x = x_coords[min_x_index]
    max_x = x_coords[(min_x_index + 1) % 2]

    min_y_index = min(range(len(y_coords)), key=y_coords.__getitem__)
    min_y = y_coords[min_y_index]
    max_y = y_coords[(min_y_index + 1) % 2]

    return np.array([[min_x, min_y], [max_x, max_y]])


def find_template_in_image(image: np.ndarray, roi: np.ndarray, detection_threshold: float,
                           detection_bounds: RegionOfInterest = RegionOfInterest.new_empty()) \
        -> RegionOfInterest:
    """
    In a given image, computes the possible locations of the
    given region (template) to find, and returns the location
    :param image: The base image, in which to find the ROI.
    :param roi: The region of interest to find in the image
    :param detection_threshold: Minimum value of the match correlation, to consider the matched region as valid
    :param detection_bounds: If set, limits the search in the given detection bounds
    :return: The xy location of the region in the image, or an empty result if no match has been found
    """
    region_matched_location = RegionOfInterest.new_empty()
    try:
        base, offset = compute_detection_offset(image, roi, detection_bounds)
    except IndexError:
        return RegionOfInterest.new_empty()

    confidence_map = cv.matchTemplate(
        base, roi,
        cv.TM_CCORR_NORMED
    )

    # fetch best match possibility location
    _, max_val, _, top_left_max_loc = cv.minMaxLoc(confidence_map)
    bottom_right_max_loc = (
        top_left_max_loc[0] + roi.shape[0], top_left_max_loc[1] + roi.shape[1]
    )

    if max_val >= detection_threshold:
        # apply offset to computed region
        matched_region = np.array((top_left_max_loc, bottom_right_max_loc))
        matched_region += offset
        # create ROI object
        region_matched_location = RegionOfInterest.from_points(image, *matched_region)

    return region_matched_location


def compute_detection_offset(base_image: np.ndarray, poi: np.ndarray, detection_bounds: RegionOfInterest) \
        -> tuple[np.ndarray, np.ndarray]:
    """
    Returns the base image and the offset to apply to the computed POI.

    This function is a bit hard to wrap up, but it essentially comes from the problem of limiting
    the search to a specific region. If you use the full image, then the computed location of the POI
    will be anchored to the full image. But to limit the search to a fraction of the image (this is what we call
    "detection bounds" across this codebase), you have to use the image of the detection bounds.
    And thus, the computed coordinates of the location of the POI will be anchored to the detection bounds'
    image. But since we draw the location on the full image, we have to offset it.

    It also handles the cases where the detection region is undefined.

    This is the essence of this function, taking care of knowing what will be the offset to apply if there is one,
    given the full frame, the POI to find and the detection bounds.
    :param base_image: The full image, taken from the video feed
    :param poi: The POI to detect
    :param detection_bounds: Where to limit the search, if not undefined
    :return: The base to use in image detection, and the offset to apply to the computed location of the tracked POI
    :raises: IndexError if POI is bigger than detection region
    """
    if detection_bounds.is_undefined():
        base: np.ndarray = base_image
        offset: np.ndarray = np.zeros(2, dtype=int)
    else:
        # return empty region if POI is bigger than detection bounds
        if (np.array(poi.shape[:2]) > np.array(detection_bounds.get_image().shape[:2])).any():
            raise IndexError("POI is bigger than detection bounds")
        base: np.ndarray = detection_bounds.get_image()
        offset: np.ndarray = detection_bounds.get_coords(RegionOfInterest.PointCoords.TOP_LEFT.value)
    return base, offset


def convert_points_to_xwyh(p1, p2) -> tuple[int, int, int, int]:
    """
    Given two points p1 and p2 describing the corners of a rectangle,
    returns the description coordinates with width and height of the
    objective rectangle.

    This function assumes that p1 is the top-left corner, and p2
    is the bottom-right corner of the rectangle.
    To normalize those points, you can use utils.normalize_region()

    :param p1: Edge corner coordinates of a point of the rectangle
    :param p2: The opposite corner's coordinates
    :return: A tuple of integers, in this order : (x, width, y, height)
    """
    x, y = p1
    w = p2[0] - p1[0]
    h = p2[1] - p1[1]
    return x, w, y, h


def ndarray_to_qimage(image: np.ndarray,
                      swap_rgb: bool = False,
                      as_qpixmap: bool = False) -> QImage | QPixmap:
    """
    Converts a NumPy array representing an RGB image
    into a QImage or a QPixmap.

    Almost everything has been taken from here : https://stackoverflow.com/a/35857856
    :param image The image to convert
    :param swap_rgb If True, swaps the order of colors
    :param as_qpixmap If True, converts the result into a QPixmap object
    """
    height, width, _ = image.shape
    bytes_per_line = 3 * width
    q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

    if swap_rgb:
        q_img = q_img.rgbSwapped()

    return q_img if not as_qpixmap else QPixmap(q_img)


def opencv_list_available_camera_ports() -> tuple[list[int], list[int], list[int]]:
    """
    Not written by me. See https://stackoverflow.com/a/62639343
    Answer's description :

    Test the ports and returns a tuple with the available ports and the ones that are working.
    :return Available ports, Working ports, Non-working ports
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []
    while len(non_working_ports) < 6:  # if there are more than 5 non-working ports stop the testing.
        camera = cv.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                working_ports.append(dev_port)
            else:
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports, non_working_ports
