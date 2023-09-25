from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from src.pattern_tracking.qt_gui.generic.GenericAssets import GenericAssets
from src.pattern_tracking.qt_gui.top_menu_bar.plot.NewPlotQDialog import NewPlotQDialog


class CreatePlotAction(QAction):

    def __init__(self,
                 tracker_manager: TrackerManager,
                 plot_widget: LivePlotterDockWidget,
                 parent: QWidget = None):
        super().__init__(parent=parent, text="Create plot")
        self._PLOTS_CONTAINER = plot_widget
        self._TRACKER_MANAGER = tracker_manager
        self.triggered.connect(self._new_plot_dialog)

    def _new_plot_dialog(self):
        if not len(self._TRACKER_MANAGER.alive_trackers().values()) >= 2:
            GenericAssets.popup_message(
                title="Error : Not enough trackers for plotting",
                message="You need to have at least 2 different trackers to start"
                        " plotting distances ! Please create a new tracker with"
                        " the tabs in the top-left of the window",
                is_error=True
            )
        else:
            dlg = NewPlotQDialog(list(self._TRACKER_MANAGER.alive_trackers().values()))

            if dlg.exec():
                self._PLOTS_CONTAINER.new_plot(dlg.get_resulting_dist_observer(), dlg.get_resulting_fps(), dlg.get_resulting_title())
