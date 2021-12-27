# kconfig_browser
KConfig Browser is a graphical application which allows you to modify KDE configuration files found in ~/.config

## Screenshot
![Screenshot of KConfigBrowser with a selected configuration file, group and key][1]

## Why
I created this little tool in order to learn Qt (in Python for now, because at the moment I don't know C++)
I kinda envied that GNOME people had the graphical dconf-editor for GConfig and KDE didn't have any graphical tools for manually editing KConfig (at least none that I've heard of)
Even though it was written in a short time, it serves it's purpose of a graphical KConfig reader/editor.

## How to install
You don't need to install it anywhere, just make sure you have the PyQt5 Python library installed and then you may run the `kdeconf.py` Python file

## How to use
Select a configuration file from the top left combobox, then select a group from the left listbox. Then, you'll see a list of keys in the right listbox. Select a key and the value will appear at bottom text input box. After changing the value, you need to click the "Save" button to save the changes. You may also click "Reload" and the text input value will be updated according to the config file contents.

## Feature requests and bug reports
If you want to request a feature or/and report a bug, please use the Issues tab

[1]: https://i.imgur.com/3aIpCNo.png
