import sys

import cv2 as cv
import numpy as np


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
    if x < 0:
        raise IndexError("x coordinate cannot be negative")
    if y < 0:
        raise IndexError("y coordinate cannot be negative")
    if x + w > image.shape[1]:
        raise IndexError("x coordinates ROI is out of bounds !")
    if y + h + 1 > image.shape[0]:
        raise IndexError("y coordinates of ROI is out of bounds !")

    return image[y: y + h + 1, x: x + w + 1]


def middle_of(p1: tuple[int, int], p2: tuple[int, int]) \
        -> tuple[int, int]:
    return int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2)


def normalize_region(pt1: tuple[int, int], pt2: tuple[int, int])\
        -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Creates a valid region by computing the minimum and maximum
    of each x and y coordinate in each point.

    This is mainly used to get valid region coordinates
    when it is selected by the user (since the start and end point can be anywhere)

    :param pt1: Tuple of x,y coordinates
    :param pt2: Tuple of x,y coordinates
    :return: Two points, where the first point is the most top-left location,
             and the other point is the most top-right location
    """
    x_coords = (pt1[0], pt2[0])
    y_coords = (pt1[1], pt2[1])

    min_x_index = min(range(len(x_coords)), key=x_coords.__getitem__)
    min_x = x_coords[min_x_index]
    max_x = x_coords[(min_x_index + 1) % 2]

    min_y_index = min(range(len(y_coords)), key=y_coords.__getitem__)
    min_y = y_coords[min_y_index]
    max_y = y_coords[(min_y_index + 1) % 2]

    return (min_x, min_y), (max_x, max_y)
