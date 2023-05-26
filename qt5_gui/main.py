import sys

from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow
from pyqtgraph import PlotDataItem, PlotItem, PlotWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()

    somePlotItem = PlotItem()
    somePlotItem.plot([(i + int(i / 4)) * i for i in range(10)])
    plotWidget = PlotWidget(plotItem=somePlotItem)

    window.setCentralWidget(plotWidget)
    window.show()

    app.exec()
