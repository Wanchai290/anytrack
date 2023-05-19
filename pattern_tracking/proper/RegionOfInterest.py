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

    @staticmethod
    def new(parent_image: np.ndarray, x: int, width: int, y: int, height: int):
        """
        Creates a new region of interest with the given parameters.
        This constructor is only an alias to create the object differently if required
        See the base constructor for more details
        """
        return RegionOfInterest(parent_image, (x, width, y, height))

    # -- Constructors

    @staticmethod
    def from_points(parent_image: np.ndarray, p1: tuple[int, int], p2: tuple[int, int]):
        """
        Alias constructor, that creates a region of interest object using two points.
        The coordinates will be normalized to a valid area, meaning that we consider both points
        as on the same diagonal, and to be two corners of the rectangle
        :param parent_image: The parent image in which the ROI is defined
        :param p1: Coordinates of a corner of the rectangle
        :param p2: Coordinates of the opposite corner to p1
        :return: A new RegionOfInterest object
        """
        p1, p2 = utils.normalize_region(p1, p2)
        x, w, y, h = utils.convert_points_to_xwyh(p1, p2)
        return RegionOfInterest.new(parent_image, x, w, y, h)

    @staticmethod
    def new_empty():
        """
        Returns a new invalid region of interest
        :return: A invalid region of interest object
        """
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
        self._xwyh: list[int, int, int, int] | np.ndarray = [0, 0, 0, 0]
        """Describe the x, y point coordinates, and width and height of the region"""
        self._coords: list[np.ndarray] = []
        """Point coordinates of the top-left and bottom-right corners of the region"""
        self._x: int = 0
        """X coordinate of the region"""
        self._width: int = 0
        """Width of the region"""
        self._y: int = 0
        """Y coordinate of the region"""
        self._height: int = 0
        """Height of the region"""
        self._image: np.ndarray = np.array([])
        """The image extracted from the parent image, using the coordinates of this region"""

        # avoid region to be outside the parent image
        xwyh = RegionOfInterest._limit_to_image(parent_image.shape, xwyh)

        self._parent_image = parent_image
        self._update_image(xwyh)

    # -- Methods

    def _update_image(self, xwyh: np.ndarray):
        self._xwyh = xwyh
        self._x, self._width, self._y, self._height = xwyh
        self._image = utils.get_roi(self._parent_image, *xwyh)

        # Top-left then bottom-right coordinates
        self._coords = [np.array((xwyh[0], xwyh[2])),
                        np.array((sum(xwyh[:2]), sum(xwyh[2:4])))]

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

        return self._x <= other._x <= sum(self._xwyh[:2]) \
            and self._y <= other._y <= sum(self._xwyh[2:4])

    def get_x(self) -> int:
        """
        Returns the y coordinate of the top-left point of this region of interest
        :return: The y coordinate of the top-left point of the ROI
        """

        return self._x

    def get_width(self) -> int:
        """
        Returns the width of this region of interest
        :return: The width of the ROI
        """
        return self._width

    def get_y(self) -> int:
        """
        Returns the y coordinate of the top-left point of this region of interest
        :return: The y coordinate of the top-left point of the ROI
        """
        return self._y

    def get_height(self) -> int:
        """
        Returns the height of this region of interest
        :return: The height of the ROI
        """
        return self._height

    def get_xwyh(self) -> np.ndarray:
        """
        Get the x, width, y and height of this region of interest
        :return: A NumPy array of length 4 containing the x, width, y and height
                 data of this region of interest, in the order described
        """
        return self._xwyh

    def is_undefined(self):
        """
        Checks whether this region of interest is valid or not
        :return: A boolean, false if this region of interest is valid
        """
        return (self._xwyh == 0).all()

    def get_parent_image(self) -> np.ndarray:
        """
        Returns the parent image in which this region of interest is defined
        :return: The parent image as a NumPy array
        """
        return self._parent_image

    def set_parent_image(self, parent_image: np.ndarray):
        """
        Replaces the current parent image with the given one.
        This has the side effect of refreshing the current image
        using the coordinates description of this object with the
        new parent image.
        Same region in terms of coordinates, but different image
        :param parent_image: The new parent image
        """
        if self._parent_image.shape != parent_image.shape:
            raise AssertionError("New parent image must have same shape as the replaced parent")
        self._parent_image = parent_image
        self._image = utils.get_roi(parent_image, *self._xwyh)

    def get_image(self) -> np.ndarray:
        """
        Returns the current image as delimited by this region of interest
        :return: The NumPy array image of this region of interest, in the parent image
        """
        return self._image

    def get_coords(self, index: int | None = None) -> list[np.ndarray] | np.ndarray:
        """
        Retrieve only 1 point, or both points from this region of interest.
        If
        :param index:
        :return:
        """
        if index is not None:
            if not 2 > RegionOfInterest.PointCoords.BOTTOM_RIGHT.value - index > -1:
                raise IndexError(
                    "Index of coordinates wanted invalid. See RegionOfInterest.PointCoords for valid indexes"
                )
            return self._coords[index]
        else:
            return self._coords

    def set_coords(self,
                   xy: np.ndarray,
                   index: int | None = None,
                   normalize: bool = False):
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
        :param normalize:
        """
        if len(xy) > 2:
            raise ValueError("Must only give 2 tuples of values for coordinates")
        if index is None:
            self._coords = xy
        else:
            if not \
                    RegionOfInterest.PointCoords.TOP_LEFT.value \
                    <= index \
                    <= RegionOfInterest.PointCoords.BOTTOM_RIGHT.value:
                raise ValueError("Can only specify top-left and bottom-right coordinates")
            self._coords[index] = xy

        # normalize points if required
        if normalize:
            self._coords = utils.normalize_region(*self._coords)

        # convert points into xwyh coordinates description
        x, w, y, h = utils.convert_points_to_xwyh(*self._coords)

        self._update_image(np.array((x, w, y, h)))

    def normalize(self):
        """
        Creates a valid region by computing the minimum and maximum
        of each x and y coordinate in each point of the ROI.

        If the points are not ordered such that p1 is the top-left corner,
        and p2 is the bottom-right corner, the function will normalize the coordinates
        so that they match what was said previously.
        Warning: Leads to point swapping bugs when used interactively

        This is mainly used to get valid region coordinates
        when it is selected by the user (since the start and end point can be anywhere)
        """
        self._coords = utils.normalize_region(*self._coords)
        x, w, y, h = utils.convert_points_to_xwyh(*self._coords)
        self._update_image(np.array((x, w, y, h)))

    def __iter__(self):
        return self._coords.__iter__()

    @staticmethod
    def _limit_to_image(parent_shape: tuple[int, int], xwyh: np.ndarray) -> np.ndarray:
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
