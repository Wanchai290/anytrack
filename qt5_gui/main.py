import sys
import time
from threading import Thread

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QSplitter
from pyqtgraph import PlotDataItem, PlotItem, PlotWidget


def update_plot(plot_data_item: PlotDataItem):
    for j in range(30):
        time.sleep(0.3)
        plot_data_item.setData([(i + int(i / 4)) * i for i in range(0, j+1)])
    return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    widgetContainer = QSplitter()

    somePlotItem = PlotItem()
    plotDataItem = somePlotItem.plot([(i + int(i / 4)) * i for i in range(10)])
    plotWidget = PlotWidget(plotItem=somePlotItem)

    widgetContainer.setOrientation(Qt.Orientation.Vertical)
    widgetContainer.addWidget(plotWidget)
    widgetContainer.addWidget(PlotWidget(plotItem=PlotItem()))

    window.setCentralWidget(widgetContainer)
    window.show()

    th = Thread(target=update_plot, args=(plotDataItem, ))
    th.start()

    app.exec()
