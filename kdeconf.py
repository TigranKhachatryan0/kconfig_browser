#!/usr/bin/env python3

import configparser
import os, sys
try:
    from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
except ImportError:
    print("error: You need to install the PyQt5 Python library first.", file=sys.stderr)
    sys.exit(1)

class KDEConfig:
    def __init__(self):
        self.exception_handler = None # This is a function which will get called every time
                                      # configparser raises an exception
        self.WRITE_ERROR      = "Could not write to the key"
        self.READ_ERROR       = "Could not read the key value"
        self.GET_KEYS_ERROR   = "Could not get keys from the selected group"
        self.GET_CONFIGS_ERROR= "Could not get a list of config files"
        self.GET_GROUPS_ERROR = "Could not get a list of groups in the config file"
    def read_config(self, file: str, group: str, key: str):
        config = configparser.ConfigParser(strict=False)
        try:
            config.read(file)
            return config[group][key]
        except Exception as e:
            if self.exception_handler:                      # If an exception handler function is assigned,
                self.exception_handler(e, self.READ_ERROR)  # Call the exception handler function
    def write_config(self, file: str, group: str, key: str, value: str):
        config = configparser.ConfigParser(strict=False)
        try:
            config.read(file)
            config[group][key] = value
            with open(file, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            if self.exception_handler:
                self.exception_handler(e, self.WRITE_ERROR)
    def get_keys(self, file: str, group: str):
        config = configparser.ConfigParser(strict=False)
        try:
            config.read(file)
            return dict(config[group])
        except Exception as e:
            if self.exception_handler:
                self.exception_handler(e, self.GET_KEYS_ERROR)
    def get_list_of_config_files(self, dir: str = f"{os.path.expanduser('~')}/.config"):
        return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.startswith("k") and f.endswith("rc")]
    def get_groups_list(self, file: str):
        config = configparser.ConfigParser(strict=False)
        try:
            config.read(file)
            return config.sections()
        except Exception as e:
            if self.exception_handler:
                self.exception_handler(e, self.GET_GROUPS_ERROR)

kde_config = KDEConfig()

class MainWindow(QtWidgets.QMainWindow):
    def resizeEvent(self, event):
        """
        Handles the resize event of the main window.

        This is used in order to change the geometry of the widgets in the main window.
        Do note, though, that I am not sure if this is the best way to do this.
        If there is a better way (which is NOT resource hungry), please let me know.

        If you're going to tell me to use layouts, I'm sorry,
        but at the moment I'm not familiar with them and find them confusing,
        but I probably will start using them someday.

        (I'm VERY new to Qt, I started self-teaching it to myself literally yesterday)
        """
        if self.resize_event_handler:
            self.resize_event_handler()
        QtWidgets.QMainWindow.resizeEvent(self, event)
    def __init__(self):
        super().__init__()
        self.resize_event_handler = None  # This is a function that will be called when the window is resized.
        self.setWindowTitle("KConfig Browser")
        self.setWindowIcon(QtGui.QIcon.fromTheme("settings-configure")) # Set the window icon to the "settings-configure" from the current theme
        self.config_files = self._generate_config_dictionary()

        self.config_files_combo = QtWidgets.QComboBox(self) # Create the combo box that will hold the list of config files
        self.config_files_combo.addItems(self.config_files.keys()) # Add the config files to the combo box
        self.config_files_combo.setCurrentIndex(0) # Set the first config file as the default (select the first item)
        self.config_files_combo.currentIndexChanged.connect(self.config_file_changed_by_user) # Connect the combo box to the function that will be called
                                                                                              # when the user changes the config file by selecting it from the combobox
        self.config_files_combo.show() # Show the combo box in the main window

        self.groups_listbox = QtWidgets.QListWidget(self) # Create the list box that will hold the groups (aka sections)
                                                          # of the config file
        self.groups_listbox.show() # Show the list box in the main window

        self.groups_listbox.currentItemChanged.connect(self.group_changed_by_user) # Connect the list box to the function that will be called
                                                                                   # when the user changes the group (aka section) by clicking on it
                                                                                   # in the list box

        self.keys_listbox = QtWidgets.QListWidget(self) # Create the list box that will hold the keys of the config file
        self.keys_listbox.currentItemChanged.connect(self.key_changed_by_user) # Connect the list box to the function that will be called
                                                                               # when the user changes the key by clicking on it in the list box
        self.keys_listbox.show() # Show the list box in the main window

        self.value_textbox = QtWidgets.QLineEdit(self) # Create the text box that will hold the value of the config file
        self.value_textbox.setEnabled(False)           # It shall be disabled by default, because there is no key selected yet
                                                       # (the user has to select a key first)
        self.value_textbox.textChanged.connect(self.value_changed_by_user) # Every time the user changes the key, the value of 
                                                                           # the key will be shown in the text box, and the user 
                                                                           # can edit it
        self.value_textbox.setPlaceholderText("Key value...")              # Set the placeholder text of the text box
        
        self.save_button = QtWidgets.QPushButton("Save", self) # Create the "Save" button
        self.save_button.clicked.connect(self.save_button_clicked) # Connect the button to the function that will be called
                                                                   # when the user clicks on the button (whenever it is enabled)
        self.save_button.setEnabled(False) # Disable the button by default, because there is no key selected yet
                                           # (the user has to select a key first)
        self.save_button.show() # Show the button in the main window

        self.reload_button = QtWidgets.QPushButton("Reload", self) # Create the "Reload" button (this button will reload the current key value)
        self.reload_button.clicked.connect(self.reload_button_clicked) # Connect the button to the function that will be called
        self.reload_button.setEnabled(False) # Disable the button by default, because there is no key selected yet
                                             # (the user has to select a key first)
        self.reload_button.show() # Show the button in the main window
        self.resize_event_handler = self._resize_window_widgets # Resizes the window widgets when the window is resized
        self.setMinimumSize(800, 600) # Set minimum window size

        # Load the first config file
        filename = self.config_files[self.config_files_combo.currentText()]
        self._load_config_file(filename)

        # Set the exception handler for the KDEConfig class
        kde_config.exception_handler = lambda exception, context: self.create_error_message(context, "Exception occurred in KDEConfig class", f"The exception is: {repr(exception)}\n\nSorry for the inconvinience. Please report this bug.")

        self.show()
    def key_changed_by_user(self):
        """
        This function is called when the user clicks on a key in the keys list box.
        It will show the value of the key in the value text box, and enable required fields (if they were disabled).
        Those fields are the value text box and the reload button.
        The save button will be disabled by default, because the key value has not been changed yet.
        """
        if self.keys_listbox.currentItem() is None:
            # The config file or the group were changed
            self.value_textbox.setText("")
            self.value_textbox.setEnabled(False)
            self.save_button.setEnabled(False)
            self.reload_button.setEnabled(False)
            return
        
        filename = self.config_files[self.config_files_combo.currentText()]
        group = self.groups_listbox.currentItem().text()
        key = self.keys_listbox.currentItem().text()

        key_value = kde_config.read_config(filename, group, key)

        self.value_textbox.setText(key_value)

        self.reload_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.value_textbox.setEnabled(True)
    def reload_button_clicked(self):
        filename = self.config_files[self.config_files_combo.currentText()]
        group = self.groups_listbox.currentItem().text()
        key = self.keys_listbox.currentItem().text()

        key_value = kde_config.read_config(filename, group, key)

        self.value_textbox.setText(key_value)
        
        self.save_button.setEnabled(False)
    def save_button_clicked(self):
        filename = self.config_files[self.config_files_combo.currentText()]
        group = self.groups_listbox.currentItem().text()
        key = self.keys_listbox.currentItem().text()
        value = self.value_textbox.text()

        kde_config.write_config(filename, group, key, value)

        self.save_button.setEnabled(False)
    def value_changed_by_user(self):
        self.save_button.setEnabled(True)
    def _load_config_file(self, config_file: str):
        self.keys_listbox.clear()      # Clear the list box that holds the keys
        self.groups_listbox.clear()    # Clear the list box that holds the groups
        self.value_textbox.setText("") # Clear the text box that holds the value of the last selected key
        
        # Traces from the old config file are now gone

        self.value_textbox.setEnabled(False) # Disable the text box,
        self.save_button.setEnabled(False)   # the "Save" button and
        self.reload_button.setEnabled(False) # the "Reload" button, because there is no key selected anymore

        filename = self.config_files[self.config_files_combo.currentText()] # Get the filename of the next config file
        items = kde_config.get_groups_list(filename)                        # Get the group list from the new config file
        if not items:
            # Error message (create_error_message) was closed by the user, ignore this
            return
        self.groups_listbox.addItems(items)                                 # Add the groups to the list box
    def config_file_changed_by_user(self):
        filename = self.config_files[self.config_files_combo.currentText()]
        self._load_config_file(filename)
    def group_changed_by_user(self):
        if self.groups_listbox.currentItem() is None:
            # Configuration file was changed, ignore this.
            return
        self.keys_listbox.clear()
        
        filename = self.config_files[self.config_files_combo.currentText()] # Get the filename of the current config file
        group = self.groups_listbox.currentItem().text()                    # Get the name of the current group
        items = kde_config.get_keys(filename,
                                    group)                                  # Get the key list from the current group
        self.keys_listbox.addItems(items.keys())                            # Add the keys to the list box
    def create_error_message(self, message, title, details):
        msg = QtWidgets.QMessageBox()                      # Create the message box
        msg.setIcon(QtWidgets.QMessageBox.Critical)        # Set the icon to "Critical" (This is an error)
        msg.setText(message)                               # Set the text of the message box
        msg.setDetailedText(details)                       # Set the detailed text of the message box. This will be shown when the user clicks on the "Show Details" button
        msg.setWindowTitle(title)                          # Set the title of the message box
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)   # Set the button that will be shown in the message box
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)     # Set the default button to the "Ok" button
        msg.exec_()                                        # Wait until the user closes the message box
    def _resize_window_widgets(self):
        PADDING_RIGHT = 10
        PADDING_LEFT = 10
        PADDING_BOTTOM = 5
        SAVE_RELOAD_BUTTON_DISTANCE = 5

        WINDOW_WIDTH = self.width()
        WINDOW_HEIGHT = self.height()

        SAVE_BUTTON_WIDTH = 100
        SAVE_BUTTON_HEIGHT = 30
        RELOAD_BUTTON_WIDTH = 100
        RELOAD_BUTTON_HEIGHT = 30

        VALUE_TEXTBOX_HEIGHT = self.value_textbox.height()
        # VALUE_TEXTBOX_WIDTH = self.value_textbox.width()  not used?

        GROUPS_LISTBOX_WIDTH = 200
        GROUPS_LISTBOX_HEIGHT = 80

        KEYS_LISTBOX_HEIGHT = WINDOW_HEIGHT - SAVE_BUTTON_HEIGHT - 30 - VALUE_TEXTBOX_HEIGHT - SAVE_BUTTON_HEIGHT
        KEYS_LISTBOX_WIDTH = WINDOW_WIDTH - 230

        self.save_button.setGeometry(QtCore.QRect(WINDOW_WIDTH - SAVE_BUTTON_WIDTH - PADDING_RIGHT,
                                                  WINDOW_HEIGHT - SAVE_BUTTON_HEIGHT - PADDING_BOTTOM,
                                                  SAVE_BUTTON_WIDTH,
                                                  SAVE_BUTTON_HEIGHT
                                                  ))
        self.reload_button.setGeometry(QtCore.QRect(WINDOW_WIDTH - SAVE_BUTTON_WIDTH - RELOAD_BUTTON_WIDTH - PADDING_RIGHT - SAVE_RELOAD_BUTTON_DISTANCE,
                                                    WINDOW_HEIGHT - RELOAD_BUTTON_HEIGHT - PADDING_BOTTOM,
                                                    RELOAD_BUTTON_WIDTH,
                                                    RELOAD_BUTTON_HEIGHT
                                                    ))
        self.value_textbox.setGeometry(QtCore.QRect(PADDING_LEFT*2 + GROUPS_LISTBOX_WIDTH,
                                                    WINDOW_HEIGHT - SAVE_BUTTON_HEIGHT - VALUE_TEXTBOX_HEIGHT - PADDING_BOTTOM,
                                                    WINDOW_WIDTH - GROUPS_LISTBOX_WIDTH - PADDING_LEFT*2 - PADDING_RIGHT,
                                                    VALUE_TEXTBOX_HEIGHT
                                                    ))
        self.groups_listbox.setGeometry(QtCore.QRect(10,
                                                     50 - PADDING_BOTTOM,
                                                     GROUPS_LISTBOX_WIDTH,
                                                     WINDOW_HEIGHT - VALUE_TEXTBOX_HEIGHT - GROUPS_LISTBOX_HEIGHT
                                                     ))
        self.keys_listbox.setGeometry(QtCore.QRect(220,
                                                   50 - PADDING_BOTTOM,
                                                   KEYS_LISTBOX_WIDTH,
                                                   KEYS_LISTBOX_HEIGHT
                                                   ))
        
        self.config_files_combo.setGeometry(QtCore.QRect(10,
                                                         10 - PADDING_BOTTOM,
                                                         GROUPS_LISTBOX_WIDTH,
                                                         30
                                                         ))
    def _generate_config_dictionary(self):
        config_files = kde_config.get_list_of_config_files()
        config_files_paths = [f"{os.path.expanduser('~')}/.config/{c}" for c in config_files]
        config_files_dict = {}
        for c,conf in enumerate(config_files):
            config_files_dict[conf] = config_files_paths[c]
        return config_files_dict

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
sys.exit(app.exec_())
