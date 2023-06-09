from PySide6.QtGui import QAction

from pattern_tracking.proper.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget


class ClearAllPlotsAction(QAction):

    def __init__(self, live_plotter_widget: LivePlotterDockWidget):
        super().__init__()
        self.triggered.connect(live_plotter_widget.clear_all)
        self.setText("Clear all plots")
