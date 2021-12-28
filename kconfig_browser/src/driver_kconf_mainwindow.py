import os

import PySide6.QtWidgets as Qw  # Importing Qt libraries with short aliases.

from kconfig_browser.src import kde_config_parser  # Use helper functions from the config module.
from kconfig_browser.src.ui_generated_files.ui_kconfig_mainwindow import Ui_MainWindow_kconf  # Import the generated UI file.
import kconfig_browser.src.helpers as helper  # Misc helpers that aren't directly related to KConfig.


class KConfMainWindow(Qw.QMainWindow, Ui_MainWindow_kconf):
    """
    This is the main window of the application.
    It inherits the Ui_MainWindow_kconf class from the auto-generated file to load the UI.
    From there, signals and slots are connected to the UI elements,
    as well as a few tweaks that aren't possible in the ui file.
    These signals and slots handle all of the logic.
    """


    def __init__(self):
        Qw.QMainWindow.__init__(self)  # Initialize the parent, but not using super() due to multiple inheritance.
        self.setupUi(self)

        # Initialize config.
        self.kde_config = kde_config_parser.KDEConfig()
        self.config_files = self._generate_config_dictionary()

        # Initialize the UI.
        self.splitter.setSizes([300, 800])  # The default size of the splitter can't be set in the designer, so here it gets a default size.
        self.comboBox_config_files.addItems(sorted(self.config_files.keys(), key=str.casefold))  # Add the config files to the combo box
        self.comboBox_config_files.setCurrentIndex(0)  # Set the first config file as the default (select the first item)

        # Connect Slots.
        self.comboBox_config_files.currentIndexChanged.connect(self.config_file_changed_by_user)  # Connect the combo box to the function that will be called
        # when the user changes the config file by selecting it from the combobox
        self.listWidget_groups.currentItemChanged.connect(self.group_changed_by_user)  # Connect the list box to the function that will be called
        # when the user changes the group (aka section) by clicking on it in the list box
        self.listWidget_keys.currentItemChanged.connect(self.key_changed_by_user)  # Connect the list box to the function that will be called
        # when the user changes the key by clicking on it in the list box
        self.lineEdit_value.textChanged.connect(self.value_changed_by_user)  # Every time the user changes the key, the value of
        # the key will be shown in the text box, and the user can edit it
        self.pushButton_save.clicked.connect(self.pushButton_save_clicked)  # Connect the button to the function that will be called
        # when the user clicks on the button (whenever it is enabled)
        self.pushButton_reload.clicked.connect(self.pushButton_reload_clicked)  # Connect the button to the function that will be called

        # Set the exception handler for the KDEConfig class
        self.kde_config.exception_handler = lambda exception, context: helper.create_error_message(context, "Exception occurred in KDEConfig class",
                                                                                              f"The exception is: {repr(exception)}\n\nSorry for the inconvenience. Please report this bug.")

        # Load the first config file
        filename = self.config_files[self.comboBox_config_files.currentText()]
        self._load_config_file(filename)


    def key_changed_by_user(self):
        """
        This function is called when the user clicks on a key in the keys list box.
        It will show the value of the key in the value text box, and enable required fields (if they were disabled).
        Those fields are the value text box and the reload button.
        The save button will be disabled by default, because the key value has not been changed yet.
        """
        if self.listWidget_keys.currentItem() is None:
            # The config file or the group were changed
            self.lineEdit_value.setText("")
            self.lineEdit_value.setEnabled(False)
            self.pushButton_save.setEnabled(False)
            self.pushButton_reload.setEnabled(False)
            return

        filename = self.config_files[self.comboBox_config_files.currentText()]
        group = self.listWidget_groups.currentItem().text()
        key = self.listWidget_keys.currentItem().text()

        key_value = self.kde_config.read_config(filename, group, key)

        self.lineEdit_value.setText(key_value)

        self.pushButton_reload.setEnabled(True)
        self.pushButton_save.setEnabled(False)
        self.lineEdit_value.setEnabled(True)


    def pushButton_reload_clicked(self):
        filename = self.config_files[self.comboBox_config_files.currentText()]
        group = self.listWidget_groups.currentItem().text()
        key = self.listWidget_keys.currentItem().text()

        key_value = self.kde_config.read_config(filename, group, key)

        self.lineEdit_value.setText(key_value)

        self.pushButton_save.setEnabled(False)


    def pushButton_save_clicked(self):
        filename = self.config_files[self.comboBox_config_files.currentText()]
        group = self.listWidget_groups.currentItem().text()
        key = self.listWidget_keys.currentItem().text()
        value = self.lineEdit_value.text()

        self.kde_config.write_config(filename, group, key, value)

        self.pushButton_save.setEnabled(False)


    def value_changed_by_user(self):
        self.pushButton_save.setEnabled(True)


    def _load_config_file(self, config_file: str):
        self.listWidget_keys.clear()  # Clear the list box that holds the keys
        self.listWidget_groups.clear()  # Clear the list box that holds the groups
        self.lineEdit_value.setText("")  # Clear the text box that holds the value of the last selected key

        # Traces from the old config file are now gone

        self.lineEdit_value.setEnabled(False)  # Disable the text box,
        self.pushButton_save.setEnabled(False)  # the "Save" button and
        self.pushButton_reload.setEnabled(False)  # the "Reload" button, because there is no key selected anymore

        filename = self.config_files[self.comboBox_config_files.currentText()]  # Get the filename of the next config file
        items = self.kde_config.get_groups_list(filename)  # Get the group list from the new config file
        if not items:
            # Error message (create_error_message) was closed by the user, ignore this
            return
        self.listWidget_groups.addItems(items)  # Add the groups to the list box


    def config_file_changed_by_user(self):
        filename = self.config_files[self.comboBox_config_files.currentText()]
        self._load_config_file(filename)


    def group_changed_by_user(self):
        if self.listWidget_groups.currentItem() is None:
            # Configuration file was changed, ignore this.
            return
        self.listWidget_keys.clear()

        filename = self.config_files[self.comboBox_config_files.currentText()]  # Get the filename of the current config file
        group = self.listWidget_groups.currentItem().text()  # Get the name of the current group
        items = self.kde_config.get_keys(filename,
                                    group)  # Get the key list from the current group
        self.listWidget_keys.addItems(items.keys())  # Add the keys to the list box


    def _generate_config_dictionary(self) -> dict[str, str]:
        config_files = self.kde_config.get_list_of_config_files()
        config_files_paths = [f"{os.path.expanduser('~')}/.config/{c}" for c in config_files]
        config_files_dict = {}
        for c, conf in enumerate(config_files):
            config_files_dict[conf] = config_files_paths[c]
        return config_files_dict
