from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QWidget, QLineEdit, QApplication, QVBoxLayout, QLabel, QComboBox, \
    QDialogButtonBox, QMessageBox

from pattern_tracking.proper.logic.tracker.AbstractTracker import AbstractTracker
from pattern_tracking.proper.logic.tracker.TrackerManager import TrackerManager


class NewTrackerQDialog(QDialog):
    """
    Dialog popup used to create a new AbstractTracker
    and assign it to a given TrackerManager
    Will display additional warnings or errors if the specified
    parameters are not valid
    """

    dialog_size = QSize(240, 160)
    """Fixed size of the dialog window"""
    window_title = "Create a new tracker"
    """Title of the popup window"""

    def __init__(self, tracker_manager: TrackerManager, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self._TRACKER_MANAGER = tracker_manager
        self._created_tracker: AbstractTracker | None = None
        """The tracker created upon closing this dialog"""

        # -- Dialog window parameters
        self.setModal(True)
        self.setWindowTitle(NewTrackerQDialog.window_title)

        # -- Window layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Tracker name"))
        self._input_name = QLineEdit(self)
        self.layout.addWidget(self._input_name)
        self.layout.addWidget(QLabel("Type of the tracker"))

        self._trackers_combobox = QComboBox(self)
        for t in TrackerManager.available_tracker_types():
            self._trackers_combobox.addItem(t.value, t)

        self.layout.addWidget(self._trackers_combobox)

        self._buttons_box = QDialogButtonBox(self)
        self._buttons_box.addButton(QDialogButtonBox.Ok)
        self._buttons_box.button(QDialogButtonBox.Ok).clicked.connect(self.validate)
        self._buttons_box.addButton(QDialogButtonBox.Cancel)
        self._buttons_box.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self.layout.addWidget(self._buttons_box)

        self.setLayout(self.layout)
        self.setFixedSize(NewTrackerQDialog.dialog_size)

    def validate(self):
        """
        Checks whether the parameters specified by the user allow
        to create a valid AbstractTracker child object.

        If a parameter causes an error, displays a popup window
        to warn the user
        """
        new_tracker_name = self._input_name.displayText()
        new_tracker_type = self._trackers_combobox.currentData()

        # Default values
        valid = False  # will get updated if operation successful
        title = "Success"
        message = f"New tracker {new_tracker_name} created successfully"
        new_tracker = None

        try:
            new_tracker = self._TRACKER_MANAGER.create_tracker(
                new_tracker_name,
                new_tracker_type
            )
            valid = new_tracker is not None

        # TODO: hmm, very much dupe
        except ValueError as err:
            title = "Error : Invalid tracker name"
            message = str(err)
        except KeyError as err:
            title = "Error : A tracker with this name already exists"
            message = str(err)
        except NotImplementedError as err:
            title = "Error : Not yet implemented, please wait !"
            message = str(err)

        # display alert dialog
        # TODO: improve GUI
        alert = QMessageBox(parent=self)
        if not valid:
            alert.addButton(QMessageBox.Close)
        else:
            alert.addButton(QMessageBox.Ok)
        alert.setWindowTitle(title)
        alert.setText(message)
        alert.exec()

        if valid:
            self._created_tracker = new_tracker
            self.accept()

    def get_created_tracker(self):
        """Returns the created tracker after closing this dialog"""
        return self._created_tracker


if __name__ == '__main__':
    app = QApplication()
    window = NewTrackerQDialog(TrackerManager())
    window.show()
    app.exec()
