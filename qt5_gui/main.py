import sys
import time
from threading import Thread

import numpy as np
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow
from pyqtgraph import PlotDataItem, PlotItem, PlotWidget


def update_plot(plot_data_item: PlotDataItem):
    time.sleep(2)
    plot_data_item.setData([(i + int(i / 4)) * i for i in range(10, 0, -1)])
    return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()

    somePlotItem = PlotItem()
    plotDataItem = somePlotItem.plot([(i + int(i / 4)) * i for i in range(10)])
    plotWidget = PlotWidget(plotItem=somePlotItem)

    window.setCentralWidget(plotWidget)
    window.show()

    th = Thread(target=update_plot, args=(plotDataItem, ))
    th.start()

    app.exec()
