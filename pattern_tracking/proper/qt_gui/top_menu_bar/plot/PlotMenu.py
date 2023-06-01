from PySide6.QtWidgets import QMenu

from pattern_tracking.proper.logic.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.logic.tracker.TrackerManager import TrackerManager
from pattern_tracking.proper.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from pattern_tracking.proper.qt_gui.top_menu_bar.plot.CreatePlotAction import CreatePlotAction


class PlotMenu(QMenu):

    def __init__(self,
                 tracker_manager: TrackerManager,
                 plot_widget: LivePlotterDockWidget):
        super().__init__(title="Plots")
        self._CREATE_PLOT_ACTION = CreatePlotAction(tracker_manager, plot_widget)
        """Creates a new plot, assuming some trackers are available"""
        self.addAction(self._CREATE_PLOT_ACTION)
