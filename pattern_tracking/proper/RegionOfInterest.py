from enum import Enum

import numpy as np

from pattern_tracking.proper import utils


class RegionOfInterest:
    """
    Represents a specific region of interest in a given image.
    Upon initialization, will limit the given coordinates
    within the bounds of the parent image, if they overflow
    """
    class PointCoords(Enum):
        """Index aliases for the RegionOfInterest class"""
        TOP_LEFT = 0
        BOTTOM_RIGHT = 1

    # -- Constructors
    @staticmethod
    def new(parent_image: np.ndarray, x: int, width: int, y: int, height: int):
        return RegionOfInterest(parent_image, (x, width, y, height))

    @staticmethod
    def from_points(parent_image: np.ndarray, p1: tuple[int, int], p2: tuple[int, int]):
        x, w, y, h = utils.convert_points_to_xwyh(p1, p2)
        return RegionOfInterest.new(parent_image, x, w, y, h)

    @staticmethod
    def new_empty():
        return RegionOfInterest(np.zeros((0, 0)), (0, 0, 0, 0))

    def __init__(self, parent_image: np.ndarray, xwyh: tuple[int, int, int, int] | np.ndarray):
        """
        Base constructor, specifies a region in a base image
        :param parent_image: The base image, in which the region is
        :param xwyh: The coordinates description of the region.
                     Order matters ! (x, width, y, height)
        """
        # error checks
        if len(xwyh) > 4:
            raise ValueError("Cannot create ROI, more than 4 items in given parameter")

        if type(xwyh) == tuple:
            xwyh = np.array(xwyh)

        # specify dummy values to initialize variables
        self.__xwyh: list[int, int, int, int] | np.ndarray = [0, 0, 0, 0]
        self.__coords: list[np.ndarray] = []
        self.__x: int = 0
        self.__width: int = 0
        self.__y: int = 0
        self.__height: int = 0
        self.__image: np.ndarray = np.array([])

        xwyh = RegionOfInterest.__limit_to_image(parent_image.shape, xwyh)

        self.__parent_image = parent_image
        self.__update_image(xwyh)

    # -- Methods

    def intersects(self, other):
        """
        Checks whether the given regions intersect
        :param other: RegionOfInterest object
        :return: True if this ROI intersects the other ROI or the other way around
        TODO: fix, won't properly work if bad points are chosen
        TODO: add tests
        """
        if self.is_undefined() or other.is_undefined():
            return False

        return self.__x <= other.__x <= sum(self.__xwyh[:2]) \
            and self.__y <= other.__y <= sum(self.__xwyh[2:4])

    def get_x(self) -> int:
        return self.__x

    def get_width(self) -> int:
        return self.__width

    def get_y(self) -> int:
        return self.__y

    def get_height(self) -> int:
        return self.__height

    def get_xwyh(self) -> np.ndarray:
        """
        Get the x, width, y and height of this region of interest
        :return: A NumPy array of length 4 containing the x, width, y and height
                 data of this region of interest, in the order described
        """
        return self.__xwyh

    def is_undefined(self):
        return (self.__xwyh == 0).all()

    def get_parent_image(self) -> np.ndarray:
        return self.__parent_image

    def set_parent_image(self, parent_image: np.ndarray):
        """
        Replaces the current parent image with the given one.
        This has the side effect of refreshing the current image
        using the coordinates description of this object with the
        new parent image.
        Same region in terms of coordinates, but different image
        :param parent_image: The new parent image
        """
        if self.__parent_image.shape != parent_image.shape:
            raise AssertionError("New parent image must have same shape as the replaced parent")
        self.__parent_image = parent_image
        self.__image = utils.get_roi(parent_image, *self.__xwyh)

    def get_image(self) -> np.ndarray:
        return self.__image

    def get_coords(self, index: int | None = None) -> list[np.ndarray] | np.ndarray:
        if index is not None:
            if not 2 > RegionOfInterest.PointCoords.BOTTOM_RIGHT.value - index > -1:
                raise IndexError("Index of coordinates wanted invalid. See RegionOfInterest.Coords for valid indexes")
            return self.__coords[index]
        else:
            return self.__coords

    def set_coords(self,
                   xy: np.ndarray,
                   index: int | None = None):
        """
        Redefine coordinates of this ROI on the parent image
        that was used when the object was created
        This will also update self.__image

        You can redefine only the top-left or bottom-right coordinate, by passing
        a tuple of coordinates in xy, and giving a proper index (0 or 1).

        If index is None, the method considers that xy is a tuple of 2 xy coordinates points.

        :param xy: Two xy coordinates, or a single xy coordinate
        :param index: Which coordinate to change (top-left or bottom-right).
                      Optional if you redefine both
        """
        if len(xy) > 2:
            raise ValueError("Must only give 2 tuples of values for coordinates")
        if index is None:
            self.__coords = xy
        else:
            if not \
                    RegionOfInterest.PointCoords.TOP_LEFT.value \
                    <= index \
                    <= RegionOfInterest.PointCoords.BOTTOM_RIGHT.value:
                raise ValueError("Can only specify top-left and bottom-right coordinates")
            self.__coords[index] = xy

        # convert points into xwyh coordinates description
        x, w, y, h = utils.convert_points_to_xwyh(*self.__coords)

        self.__update_image(np.array((x, w, y, h)))

    def normalize(self):
        """
        Creates a valid region by computing the minimum and maximum
        of each x and y coordinate in each point of the ROI.

        This is mainly used to get valid region coordinates
        when it is selected by the user (since the start and end point can be anywhere)

        """
        pt_start, pt_end = utils.normalize_region(*self.__coords)

        # update attributes accordingly
        x, w, y, h = utils.convert_points_to_xwyh(pt_start, pt_end)

        self.__update_image(np.array((x, w, y, h)))

    def __getitem__(self, key) -> int:
        RegionOfInterest.__index_check(key)
        return self.__xwyh[key]

    def __iter__(self):
        return self.__coords.__iter__()  # todo: iz work good ?

    @classmethod
    def __index_check(cls, i):
        if not cls.PointCoords.TOP_LEFT <= i <= cls.PointCoords.BOTTOM_RIGHT:
            raise IndexError("Index must be between 0 and 1 included")

    @staticmethod
    def __limit_to_image(parent_shape: tuple[int, int], xwyh: np.ndarray) -> np.ndarray:
        """
        Binds the given coordinates (x,y and width, height) to the given
        parent shape. If the coordinates go beyond the parent shape,
        they will be limited to the said shape
        :param parent_shape: The shape to not go beyond
        :param xwyh: Coordinates description (x, width, y, height)
        :return: The limited modified coordinates
        """
        x, w, y, h = xwyh

        x_edge = x + w
        y_edge = y + h
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x_edge > parent_shape[1]:
            w = parent_shape[1]
        if y_edge > parent_shape[0]:
            h = parent_shape[0]

        return np.array((x, w, y, h))

    def __update_image(self, xwyh: np.ndarray):
        self.__xwyh = xwyh
        self.__x, self.__width, self.__y, self.__height = xwyh
        self.__image = utils.get_roi(self.__parent_image, *xwyh)

        # Top-left then bottom-right coordinates
        self.__coords = [np.array((xwyh[0], xwyh[2])),
                         np.array((sum(xwyh[:2]), sum(xwyh[2:4])))]

    def offset(self, offset: np.ndarray) -> np.ndarray:
        """
        Offsets the coordinates of the current object's points
        Does not update the other attributes
        :param offset: The offset to apply to each point
        :return: Top-left and bottom-right coordinates of the region's coordinates
                 modified using the given offset
        """
        return np.array(
            [self.__coords[i] + offset for i in range(len(self.__coords))]
        )
