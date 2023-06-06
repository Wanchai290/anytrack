import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QHBoxLayout
from pyqtgraph import PlotWidget

from pattern_tracking.proper.logic.DistanceComputer import DistanceComputer


class LivePlotterDockWidget(QDockWidget):
    """
    Dock widget that contains a collection of PlotWidget objects, alongside their
    affected DistanceComputer object that give them the additional data to plot to the user
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._plot_widgets: dict[DistanceComputer, PlotWidget] = {}

        # Empty widget displayed when there is no plot available
        tmp_widget = QWidget()
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(QLabel("No plot defined !"))
        tmp_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        tmp_widget.setLayout(tmp_layout)

        self.setWidget(tmp_widget)
        self.setMinimumSize(800, 240)
        self.show()

    def new_plot(self, dist_computer: DistanceComputer):
        """Create a new PlotWidget to be displayed, and updated in real-time"""
        set_new_as_active = len(self._plot_widgets) == 0
        plot_widget = PlotWidget()
        plot_widget.plotItem.plot([dist_computer.distance()])
        self._plot_widgets[dist_computer] = plot_widget

        if set_new_as_active:
            self.setWidget(self._plot_widgets[dist_computer])

    def update(self):
        """Updates all the current plots with new data from their trackers"""
        for (dist_computer, plot_widget) in self._plot_widgets.items():
            d = dist_computer.distance()
            if d != DistanceComputer.ERR_DIST:
                # a PlotItem can contain multiple PlotDataItem objects
                # we only put 1 unique PlotDataItem in each plot
                plot_data_item = plot_widget.plotItem.listDataItems()[0]
                _, data_y = plot_data_item.getData()
                data_y = np.append(data_y, d)
                plot_data_item.setData(data_y)
