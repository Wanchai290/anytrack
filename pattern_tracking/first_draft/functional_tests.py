import cv2 as cv

from pattern_tracking.first_draft.utils import alpha_blend, get_roi


def test_alpha_blend():
    fore = cv.imread('test_assets/KTIfd.png', cv.IMREAD_UNCHANGED)
    back = cv.imread('test_assets/Tyxgv.png', cv.IMREAD_UNCHANGED)

    res = alpha_blend(fg=back, bg=fore)
    cv.imshow('', res)
    cv.waitKey(-1)
    cv.destroyAllWindows()


def test_get_roi():
    messi = cv.imread("test_assets/roi.jpg")
    ball = get_roi(messi, x=330, w=60, y=219, h=60)
    cv.imshow('', ball)
    cv.waitKey(-1)
    cv.destroyAllWindows()


if __name__ == '__main__':
    # test_alpha_blend()
    test_get_roi()
