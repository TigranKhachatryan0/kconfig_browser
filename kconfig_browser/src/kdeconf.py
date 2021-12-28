#!/usr/bin/env python3
import sys


try:
    import PySide6.QtWidgets as Qw
    import PySide6.QtCore as Qc
except ImportError:
    print("error: You need to install PySide6 first.", file=sys.stderr)  # Can be installed using the package manager (preferred) or pip.
    sys.exit(1)

from kconfig_browser.src.driver_kconf_mainwindow import KConfMainWindow

"""
This is the bootloader file that starts the application.
Alternatively, it can be named main.py, but I kept this to not break your "how to run" instructions.
"""


def main():
    # Enable HiDPI support.
    Qw.QApplication.setAttribute(Qc.Qt.AA_EnableHighDpiScaling, True)
    Qw.QApplication.setAttribute(Qc.Qt.AA_UseHighDpiPixmaps, True)

    # Launch the main window.
    app = Qw.QApplication(sys.argv)

    window = KConfMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
