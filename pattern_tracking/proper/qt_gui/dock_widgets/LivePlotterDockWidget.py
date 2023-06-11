from threading import Lock

import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QHBoxLayout
from pyqtgraph import PlotWidget, PlotItem

from pattern_tracking.proper.logic.DistanceComputer import DistanceComputer
from pattern_tracking.proper.qt_gui.top_menu_bar.plot.DistancePlotWidget import DistancePlotWidget


class LivePlotterDockWidget(QDockWidget):
    """
    Dock widget that contains a collection of PlotWidget objects, alongside their
    affected DistanceComputer object that give them the additional data to plot to the user
    """

    WIDGET_SIZE = 800, 240

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._mutex = Lock()

        self._plot_widgets: dict[DistanceComputer, DistancePlotWidget] = {}
        self._current_frame_number = 0
        # Empty widget displayed when there is no plot available
        tmp_widget = QWidget()
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(QLabel("No plot defined !"))
        tmp_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        tmp_widget.setLayout(tmp_layout)

        self.setWidget(tmp_widget)
        self.setMinimumSize(*LivePlotterDockWidget.WIDGET_SIZE)
        self.show()

    def new_plot(self, dist_computer: DistanceComputer, feed_fps: int):
        """Create a new PlotWidget to be displayed, and updated in real-time"""
        set_new_as_active = len(self._plot_widgets) == 0
        plot_widget = DistancePlotWidget(feed_fps)

        # Here, this mutex was required because of the self._current_frame_number attribute
        # it only changes when called by the update_plots() method.
        self._mutex.acquire()
        LivePlotterDockWidget.plot_new_point(plot_widget, dist_computer.distance(), self._current_frame_number,
                                             update=False)
        self._mutex.release()
        self._plot_widgets[dist_computer] = plot_widget

        if set_new_as_active:
            self.setWidget(self._plot_widgets[dist_computer])

    def update_plots(self, frame_number: int):
        """Updates all the current plots with new data from their trackers"""
        super().update()
        self._mutex.acquire()
        self._current_frame_number = frame_number
        for (dist_computer, plot_widget) in self._plot_widgets.items():
            distance = dist_computer.distance()
            if distance != DistanceComputer.ERR_DIST:
                plot_widget.plot_new_point(plot_widget.get_feed_fps(), distance, frame_number)
        self._mutex.release()

    def clear_all(self):
        self._mutex.acquire()
        for (dist_computer, plot_widget) in self._plot_widgets.items():
            plot_widget.clear()
        self._mutex.release()

    @classmethod
    def plot_new_point(cls, plot_widget: DistancePlotWidget, distance: float, current_frame_number: int,
                       update: bool = False):
        """Plots a new point for a PlotWidget object"""
        # plot_widget.plot_new_point(plot_widget.get_fps(), distance, current_frame_number)
        # new_x, new_y = LivePlotterDockWidget.new_point_data(feed_fps, distance, current_frame_number)
        # if update:
        #     # a PlotItem can contain multiple PlotDataItem objects
        #     # we only put 1 unique PlotDataItem in each plot
        #     plot_data_item = plot_widget.plotItem.listDataItems()[0]
        #     data_x, data_y = plot_data_item.getData()
        #     data_x = np.append(data_x, new_x)
        #     data_y = np.append(data_y, int(new_y))
        #     plot_data_item.setData(data_x, data_y)
        #
        # else:
        #     plot_widget.plotItem.plot([new_x], [new_y])

