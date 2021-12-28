"""
This module holds helper functions that can be used for multiple purposes.
"""
import PySide6.QtWidgets as Qw


def create_error_message(message: str, title: str, details: str):
    msg = Qw.QMessageBox()  # Create the message box
    msg.setIcon(Qw.QMessageBox.Critical)  # Set the icon to "Critical" (This is an error)
    msg.setText(message)  # Set the text of the message box
    msg.setDetailedText(details)  # Set the detailed text of the message box. This will be shown when the user clicks on the "Show Details" button
    msg.setWindowTitle(title)  # Set the title of the message box
    msg.setStandardButtons(Qw.QMessageBox.Ok)  # Set the button that will be shown in the message box
    msg.setDefaultButton(Qw.QMessageBox.Ok)  # Set the default button to the "Ok" button
    msg.exec()  # Wait until the user closes the message box
