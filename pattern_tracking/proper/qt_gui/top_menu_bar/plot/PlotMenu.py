from PySide6.QtWidgets import QMenu

from pattern_tracking.proper.logic.tracker.TrackerManager import TrackerManager
from pattern_tracking.proper.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from pattern_tracking.proper.qt_gui.top_menu_bar.plot.ClearActivePlotAction import ClearActivePlotAction
from pattern_tracking.proper.qt_gui.top_menu_bar.plot.ClearAllPlotsAction import ClearAllPlotsAction
from pattern_tracking.proper.qt_gui.top_menu_bar.plot.CreatePlotAction import CreatePlotAction


class PlotMenu(QMenu):

    def __init__(self,
                 tracker_manager: TrackerManager,
                 plot_docker_widget: LivePlotterDockWidget):
        super().__init__(title="Plots")
        self._CREATE_PLOT_ACTION = CreatePlotAction(tracker_manager, plot_docker_widget)
        """Creates a new plot, assuming some trackers are available"""
        self._CLEAR_ACTIVE_PLOT_ACTION = ClearActivePlotAction(plot_docker_widget)
        """Clears the currently displayed plot"""
        self._CLEAR_ALL_PLOTS_ACTION = ClearAllPlotsAction(plot_docker_widget)
        """Clears all plots contained in the QDockerWidget that contains the plots"""
        self.addAction(self._CREATE_PLOT_ACTION)
        self.addAction(self._CLEAR_ALL_PLOTS_ACTION)
        self.addAction(self._CLEAR_ACTIVE_PLOT_ACTION)
