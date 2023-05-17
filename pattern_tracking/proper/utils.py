import sys

import cv2 as cv
import numpy as np

from pattern_tracking.proper.RegionOfInterest import RegionOfInterest


def alpha_blend(bg: cv.Mat | np.ndarray, fg: cv.Mat | np.ndarray) -> np.ndarray:
    """
    Merges two RGBA images together, by applying the image
    'fg' on top of 'bg'

    See the following link for more details :
    https://stackoverflow.com/questions/60398939/how-to-do-alpha-compositing-with-a-list-of-rgba-data-in-numpy-arrays
    :param bg: An RGBA image matrix
    :param fg: The other RGBA image matrix to blend in
    :return: An image with fg applied on top of bg
    """

    # alpha channels are normalized to a 0..1 range
    # required because of the alpha blending formula
    # see https://en.wikipedia.org/wiki/Alpha_compositing#Description
    # ("over" alpha compositing formula)
    try:
        bg_alpha = bg[..., 3] / 255.0
        fg_alpha = fg[..., 3] / 255.0
    except IndexError:
        print("One of the images is not RGBA !", file=sys.stderr)
        exit(100)

    # extraction of RGB channels
    bg_rgb = bg[..., :3]
    fg_rgb = fg[..., :3]

    # computing resulting channels
    result_alpha = fg_alpha + bg_alpha * (1 - fg_alpha)
    result_alpha[np.where(result_alpha == 0)] = 1  # avoid div by zero

    # note: broadcasting of the alpha channels is required here, so that numpy can
    # automatically multiply the rgb array and alpha array
    # you can learn more about broadcasting numpy arrays on the official docs
    # https://numpy.org/doc/stable/user/basics.broadcasting.html
    result_rgb = 1.0 * (
            fg_rgb * fg_alpha[:, :, np.newaxis]
            + bg_rgb * bg_alpha[:, :, np.newaxis]
            * (1 - fg_alpha[:, :, np.newaxis])
    ) / result_alpha[:, :, np.newaxis]

    # merging into result image
    # result should always be an RGBA image here
    result = np.dstack((result_rgb, result_alpha * 255)).astype(np.uint8)

    return result


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


def middle_of(p1: tuple[int, int], p2: tuple[int, int]) \
        -> tuple[int, int]:
    return int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2)


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

    if detection_bounds.is_undefined():
        base: np.ndarray = image
        offset: np.ndarray = np.zeros((1, 2), dtype=int)
    else:
        # if (detection_bounds.get_parent_image() != image).any():
        #     raise AssertionError("Backing image of detection bounds and given image is not the same !")
        base: np.ndarray = detection_bounds.get_image()
        offset: np.ndarray = detection_bounds.get_coords(RegionOfInterest.PointCoords.TOP_LEFT.value)

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


def convert_points_to_xwyh(p1, p2) -> tuple[int, int, int, int]:
    p1, p2 = normalize_region(p1, p2)
    x, y = p1
    w = p2[0] - p1[0]
    h = p2[1] - p1[1]
    return x, w, y, h
