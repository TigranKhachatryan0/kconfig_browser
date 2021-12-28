"""
This is a collection of functions to read and write the kde configuration file.
"""

import configparser
import os
import re



"""
This class was originally created by the GitHub user Zren
The original class can be found here: https://github.com/Zren/breeze-alphablack/blame/master/desktoptheme.py#L21
"""



class KdeConfigParser(configparser.ConfigParser):
    def __init__(self, filename, strict: bool = True):
        super().__init__(strict=strict)

        # Keep case sensitive keys
        # http://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
        self.optionxform = str

        # Parse SubSections as "Sub][Sections"
        self.SECTCRE = re.compile(r"\[(?P<header>.+?)]\w*$")

        self.filename = filename


    # self.read(self.filename)
    def set(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)
        super().set(section, option, str(value))


    def setProp(self, key, value):
        section, option = key.split('.', 1)
        return self.set(section, option, value)


    def getProp(self, key):
        section, option = key.split('.', 1)
        return self.get(section, option)


    def default(self, section, option, value):
        if not self.has_option(section, option):
            self.set(section, option, value)


    def save(self):
        with open(self.filename, 'w') as fp:
            self.write(fp, space_around_delimiters=False)



class KDEConfig:
    def __init__(self):
        self.exception_handler = None  # This is a function which will get called every time
        # configparser raises an exception
        self.WRITE_ERROR = "Could not write to the key"
        self.READ_ERROR = "Could not read the key value"
        self.GET_KEYS_ERROR = "Could not get keys from the selected group"
        self.GET_CONFIGS_ERROR = "Could not get a list of config files"
        self.GET_GROUPS_ERROR = "Could not get a list of groups in the config file"


    def read_config(self, file: str, group: str, key: str):
        group = group.replace("․", "][")
        config = KdeConfigParser(file, strict=False)
        try:
            config.read(file)
            return config[group][key]
        except Exception as e:
            if self.exception_handler:  # If an exception handler function is assigned,
                self.exception_handler(e, self.READ_ERROR)  # Call the exception handler function


    def write_config(self, file: str, group: str, key: str, value: str):
        group = group.replace("․", "][")
        config = KdeConfigParser(file, strict=False)
        try:
            config.read(file)
            config[group][key] = value
            with open(file, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            if self.exception_handler:
                self.exception_handler(e, self.WRITE_ERROR)


    def get_keys(self, file: str, group: str):
        group = group.replace("․", "][")
        config = KdeConfigParser(file, strict=False)
        try:
            config.read(file)
            return dict(config[group])
        except Exception as e:
            if self.exception_handler:
                self.exception_handler(e, self.GET_KEYS_ERROR)


    @staticmethod
    def get_list_of_config_files(path: str = str(os.path.expanduser('~/.config'))):  # Using path instead of dir because dir is a builtin function.
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith("rc") and f not in ("gtkrc",)]


    def get_groups_list(self, file: str):
        config = KdeConfigParser(file, strict=False)
        try:
            config.read(file)
            return [s.replace("][", "․") for s in config.sections()]
        except Exception as e:
            if self.exception_handler:
                self.exception_handler(e, self.GET_GROUPS_ERROR)