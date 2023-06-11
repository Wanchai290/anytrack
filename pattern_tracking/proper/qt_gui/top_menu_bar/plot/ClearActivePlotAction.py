from PySide6.QtGui import QAction

from pattern_tracking.proper.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget


class ClearActivePlotAction(QAction):

    def __init__(self, plot_widget_dock: LivePlotterDockWidget):
        super().__init__()
        self.triggered.connect(plot_widget_dock.clear_active_plot)
        self.setText("Clear active plot")
