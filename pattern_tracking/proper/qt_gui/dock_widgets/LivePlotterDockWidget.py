from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QGraphicsView, QHBoxLayout
from pyqtgraph import PlotWidget, PlotItem


class LivePlotterDockWidget(QDockWidget):

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self._plot_widgets: list[PlotWidget] = []

        tmp_widget = QWidget()
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(QLabel("No plot defined !"))
        tmp_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        tmp_widget.setLayout(tmp_layout)
        self.setWidget(tmp_widget)
        self.setMinimumSize(800, 240)
        self.show()
