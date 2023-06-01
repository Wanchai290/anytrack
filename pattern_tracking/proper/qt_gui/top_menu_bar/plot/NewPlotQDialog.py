from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QWidget, QComboBox, QVBoxLayout, QDialogButtonBox, QLabel, QHBoxLayout, \
    QApplication, QMessageBox, QStyle

from pattern_tracking.proper.qt_gui.generic.GenericAssets import GenericAssets
from pattern_tracking.proper.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.tracker.TemplateTracker import TemplateTracker


class NewPlotQDialog(QDialog):
    """
    Custom QDialog to ask the user which trackers he wants to link together,
    so he can see the live distance between the POIs of those two trackers
    """

    def __init__(self, available_trackers: list[AbstractTracker], parent: QWidget = None):
        super().__init__(parent)
        self._tracker_one: AbstractTracker | None = None
        self._tracker_two: AbstractTracker | None = None

        # -- Window layout
        self._layout = QVBoxLayout()
        self._tracker_choice_one = QComboBox()
        self._tracker_choice_two = QComboBox()
        for t in available_trackers:
            self._tracker_choice_one.addItem(t.get_name(), t.get_id())
            self._tracker_choice_two.addItem(t.get_name(), t.get_id())

        self._layout.addWidget(QLabel("Select the two trackers to link"))
        layout_choice_one = QHBoxLayout()
        layout_choice_one.addWidget(QLabel("Tracker one"))
        layout_choice_one.addWidget(self._tracker_choice_one)
        self._layout.addLayout(layout_choice_one)

        layout_choice_two = QHBoxLayout()
        layout_choice_two.addWidget(QLabel("Tracker two"))
        layout_choice_two.addWidget(self._tracker_choice_two)
        self._layout.addLayout(layout_choice_two)

        # TODO: kind of a copy/paste from NewTrackerQDialog, should I create a parent class ?
        self._buttons_box = QDialogButtonBox(self)
        self._buttons_box.addButton(QDialogButtonBox.Ok)
        self._buttons_box.button(QDialogButtonBox.Ok).clicked.connect(self.validate)
        self._buttons_box.addButton(QDialogButtonBox.Cancel)
        self._buttons_box.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self._layout.addWidget(self._buttons_box)

        self.setLayout(self._layout)

    def validate(self):
        """
        Checks whether the given parameters are valid, and ends the dialog
        window by emitting the base accept() signal
        """
        selected_tracker_one = self._tracker_choice_one.currentData()
        selected_tracker_two = self._tracker_choice_two.currentData()

        popup_title = "Success"
        popup_message = "A new plot has been created"
        valid = False

        if selected_tracker_one == selected_tracker_two:
            popup_title = "Error : Same tracker"
            popup_message = "The two trackers must be different"

        else:
            valid = True

        GenericAssets.popup_message(popup_title, popup_message, is_error=not valid)

        if valid:
            self.accept()

    def get_trackers_to_link(self) -> tuple[AbstractTracker, AbstractTracker]:
        """
        Get the trackers chosen by the user
        Should not be called until the choices have been validated
        :return: the two trackers that we want to link together, to plot the distance between their tracked POIs
        """
        return self._tracker_choice_one.currentData(), self._tracker_choice_two.currentData()


if __name__ == '__main__':
    app = QApplication()
    window = NewPlotQDialog([TemplateTracker("a"), TemplateTracker("g")])
    window.exec()
