import sys

import cv2 as cv
import numpy as np


def alpha_blend(src1: cv.Mat, src2: cv.Mat) -> np.ndarray:
    """
    Merges two RGBA images together, in the OpenCV type

    See the following link for more details :
    https://stackoverflow.com/questions/60398939/how-to-do-alpha-compositing-with-a-list-of-rgba-data-in-numpy-arrays
    :param src1: An RGBA image matrix
    :param src2: The other RGBA image matrix to blend in
    :return: An image with src1 applied on top of src2
    """

    # alpha channels are normalized to a 0..1 range
    try:
        src1_alpha = src1[..., 3] / 255.0
        src2_alpha = src2[..., 3] / 255.0
    except IndexError:
        print("One of the images is not RGBA !", file=sys.stderr)
        exit(100)

    # extraction of RGB channels
    src1_rgb = src1[..., :3]
    src2_rgb = src2[..., :3]

    # computing resulting channels
    result_alpha = src1_alpha + src2_alpha * (1 - src1_alpha)

    # note: broadcasting of the alpha channels is required here, so that numpy can
    # automatically multiply the rgb array and alpha array
    # you can learn more about broadcasting numpy arrays on the official docs
    # https://numpy.org/doc/stable/user/basics.broadcasting.html
    result_rgb = 1.0 * (
            src1_rgb * src1_alpha[:, :, np.newaxis]
            + src2_rgb * src2_alpha[:, :, np.newaxis]
            * (1 - src1_alpha[:, :, np.newaxis])
        ) / result_alpha[:, :, np.newaxis]

    # merging into result image
    # result should always be an RGBA image here
    # result = np.zeros((*result_rgb.shape[:2], 4))
    # result[:, :, :3] = result_rgb
    # result[:, :, 3] = result_alpha

    result = np.dstack((result_rgb, result_alpha*255)).astype(np.uint8)

    return result


if __name__ == '__main__':
    fg = cv.imread('assets/KTIfd.png', cv.IMREAD_UNCHANGED)
    bg = cv.imread('assets/Tyxgv.png', cv.IMREAD_UNCHANGED)

    res = alpha_blend(bg, fg)
    cv.imshow('', res)
    cv.waitKey(-1)
    cv.destroyAllWindows()
