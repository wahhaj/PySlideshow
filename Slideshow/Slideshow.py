#!/usr/bin/env python

import sys
import platform

import PySide
from PySide.QtGui import QApplication, QMainWindow, QFileDialog

__version__ = '0.0.1'

from ui_slideshow import Ui_MainWindow
import qrc_slideshow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.actionExit.triggered.connect(self.close)
        self.actionOpen_directory.triggered.connect(self.choose_dir)

    def choose_dir(self):
        image_dir = QFileDialog.getExistingDirectory(self, self.tr("Choose directory"))

        print(image_dir)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()