import sys

import cv2 as cv
import numpy as np


def alpha_blend(bg: cv.Mat, fg: cv.Mat) -> np.ndarray:
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
    result = np.dstack((result_rgb, result_alpha*255)).astype(np.uint8)

    return result


if __name__ == '__main__':
    fore = cv.imread('assets/KTIfd.png', cv.IMREAD_UNCHANGED)
    back = cv.imread('assets/Tyxgv.png', cv.IMREAD_UNCHANGED)

    res = alpha_blend(fg=back, bg=fore)
    cv.imshow('', res)
    cv.waitKey(-1)
    cv.destroyAllWindows()
