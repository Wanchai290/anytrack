from typing import Any

from pyqtgraph import PlotWidget
import numpy as np


class DistancePlotWidget(PlotWidget):
    """
    This custom widget displays a live distance graph.
    Note that we assume that we only use ONE PlotDataItem
    in this widget's PlotData.
    """

    def __init__(self,
                 feed_fps: int,
                 parent: Any = None,
                 background: str = 'default',
                 plotItem: Any = None,
                 **kargs: Any) -> None :
        super().__init__(parent, background, plotItem, **kargs)
        self._feed_fps = feed_fps
        self._initialized = False

    def get_feed_fps(self):
        return self._feed_fps

    def plot_new_point(self, feed_fps: int, distance: float,
                       current_frame_number: int):
        """Plots a new point with the given data to this plot"""
        new_x, new_y = DistancePlotWidget.new_point_data(feed_fps, distance, current_frame_number)

        # the only way to create a PlotDataItem for a PlotItem
        # is calling PlotItem.plot()
        # we need to know whether we have to update the plot
        # or to initialize the PlotDataItem behind
        # we check whether there is one PlotDataItem in this PlotItem
        # below line is similar to `if self.plotItem.listDataItems() != []`
        if self.plotItem.listDataItems():
            # a PlotItem can contain multiple PlotDataItem objects
            # we only put 1 unique PlotDataItem in each plot
            plot_data_item = self.plotItem.listDataItems()[0]
            data_x, data_y = plot_data_item.getData()
            data_x = np.append(data_x, new_x)
            data_y = np.append(data_y, int(new_y))
            plot_data_item.setData(data_x, data_y)

        else:
            self.plotItem.plot([new_x], [new_y])
            self._initialized = True

    def clear(self):
        """Removes the only PlotDataItem used in this PlotWidget"""
        self.plotItem.clear()
        self._initialized = False

    @classmethod
    def new_point_data(cls, feed_fps: int, distance: float, current_frame_number: int):
        """Contains the current formulas used to compute new values on the x and y-axis"""
        new_x = current_frame_number / feed_fps
        new_y = distance
        return new_x, new_y
