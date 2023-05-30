from abc import ABC, abstractmethod

from PySide6.QtGui import QAction


class RemoteQActionsInterface(ABC):
    """
    Defines that any child inheriting this class should have
    one or multiple QAction objects that can be triggered remotely
    from any source to execute operations on the child class

    This doesn't define what actions can be performed, or how many should
    be available, but rather the fact that the child class has some remotely
    trigger-able actions
    """

    @abstractmethod
    def init_qt_actions(self):
        pass

    @abstractmethod
    def get_qt_actions(self) -> dict[str, QAction]:
        pass
