from typing import Any

from pyqtgraph import PlotWidget


class DistancePlotWidget(PlotWidget):

    def __init__(self,
                 feed_fps: int,
                 parent: Any = None,
                 background: str = 'default',
                 plotItem: Any = None,
                 **kargs: Any) -> None :
        super().__init__(parent, background, plotItem, **kargs)
        self._fps = feed_fps

    def get_fps(self):
        return self._fps
