from queue import Queue
from threading import Event

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QLineEdit, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox

from comm_protocol.FrameTCPClient import FrameTCPClient
from comm_protocol.server.FrameTCPServer import FrameTCPServer
from pattern_tracking.proper.logic.video.FramesFromDistantServer import FramesFromDistantServer
from pattern_tracking.proper.qt_gui.generic.GenericAssets import GenericAssets


class NewServerFeedQDialog(QDialog):
    """
    Dialog to create a new FrameTCPServer object
    and use it as the main video feed in the application
    """
    def __init__(self, halt_event: Event, parent: QWidget = None):
        super().__init__(parent)
        self._connection_result: FrameTCPServer | None = None
        """The resulting connection object created"""
        self._halt_event = halt_event
        self._ip_address_line_edit = QLineEdit()
        self._port_line_edit = QLineEdit()
        self._port_line_edit.setText(str(FrameTCPServer.DEFAULT_PORT))
        self._port_line_edit_validator = QIntValidator(1024, (2**16)-1, self)
        self._port_line_edit.setValidator(self._port_line_edit_validator)

        self._layout = QVBoxLayout()

        layout_ip = QHBoxLayout()
        layout_ip.addWidget(QLabel("IP Address"))
        layout_ip.addWidget(self._ip_address_line_edit)
        self._layout.addLayout(layout_ip)

        layout_port = QHBoxLayout()
        layout_port.addWidget(QLabel("IP Address"))
        layout_port.addWidget(self._port_line_edit)
        self._layout.addLayout(layout_port)

        self._buttons_box = QDialogButtonBox(self)
        self._buttons_box.addButton(QDialogButtonBox.Ok)
        self._buttons_box.button(QDialogButtonBox.Ok).clicked.connect(self.validate)
        self._buttons_box.addButton(QDialogButtonBox.Cancel)
        self._buttons_box.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self._layout.addWidget(self._buttons_box)

        self.setLayout(self._layout)

    def validate(self):
        valid = False
        try:
            result = FramesFromDistantServer(self._ip_address_line_edit.text(), int(self._port_line_edit.text()), self._halt_event)
            valid = True
        except OSError as err:
            GenericAssets.popup_message(
                "Invalid settings",
                "The IP address and/or port specified is invalid, please change it. \n"
                f"{err}\n"
                f"If it couldn't assign the address, checked that you are properly connected via an Ethernet cable.",
                valid,
                self
            )

        if valid:
            self._connection_result = result
            self.accept()

    def get_connection_result(self):
        return self._connection_result
