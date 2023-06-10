from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog, QWidget, QComboBox, QVBoxLayout, QDialogButtonBox, QLabel, QHBoxLayout, \
    QApplication, QLineEdit

from pattern_tracking.proper.logic.DistanceComputer import DistanceComputer
from pattern_tracking.proper.qt_gui.generic.GenericAssets import GenericAssets
from pattern_tracking.proper.logic.tracker import AbstractTracker
from pattern_tracking.proper.logic.tracker import TemplateTracker


class NewPlotQDialog(QDialog):
    """
    Custom QDialog to ask the user which trackers he wants to link together,
    so he can see the live distance between the POIs of those two trackers
    """

    def __init__(self, available_trackers: list[AbstractTracker], parent: QWidget = None):
        super().__init__(parent)

        self._dist_observer_result: DistanceComputer | None = None
        """The resulting object created when the user closes the dialog"""
        self._tracker_one: AbstractTracker | None = None
        """Some tracker to be linked to Other"""
        self._tracker_two: AbstractTracker | None = None
        """The other tracker to be linked to Some"""
        self._feed_fps_result: int | None = None
        """The camera feed FPS"""

        # -- Window layout
        self._layout = QVBoxLayout()
        self._tracker_choice_one = QComboBox()
        self._tracker_choice_two = QComboBox()
        for t in available_trackers:
            self._tracker_choice_one.addItem(t.get_name(), t)
            self._tracker_choice_two.addItem(t.get_name(), t)

        layout_plot_name = QHBoxLayout()
        layout_plot_name.addWidget(QLabel("Name of the plot window"))
        self._plot_name_line_edit = QLineEdit()
        layout_plot_name.addWidget(self._plot_name_line_edit)
        self._layout.addLayout(layout_plot_name)

        layout_feed_fps = QHBoxLayout()
        layout_feed_fps.addWidget(QLabel("FPS (Frames Per Second) of the camera"))
        self._feed_fps_line_edit = QLineEdit()
        self._feed_fps_validator = QIntValidator(0, 2**15, self)
        self._feed_fps_line_edit.setValidator(self._feed_fps_validator)
        layout_feed_fps.addWidget(self._feed_fps_line_edit)
        self._layout.addLayout(layout_feed_fps)

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
        plot_name = self._plot_name_line_edit.text().strip()

        popup_title = "Success"
        popup_message = "A new plot has been created"
        valid = False

        try:
            feed_fps = int(self._feed_fps_line_edit.text())
            dist_observer = DistanceComputer(
                plot_name,
                selected_tracker_one,
                selected_tracker_two
            )
            valid = True
        except ValueError as err:
            popup_title = "Error: Invalid parameters"
            popup_message = str(err)

        GenericAssets.popup_message(popup_title, popup_message, is_error=not valid)

        if valid:
            self._dist_observer_result = dist_observer
            self._feed_fps_result = feed_fps
            self.accept()

    def get_resulting_dist_observer(self):
        """:return: The DistanceObserver linking two trackers together"""
        return self._dist_observer_result

    def get_resulting_fps(self):
        return self._feed_fps_result


if __name__ == '__main__':
    app = QApplication()
    window = NewPlotQDialog([TemplateTracker("a"), TemplateTracker("g")])
    window.exec()
