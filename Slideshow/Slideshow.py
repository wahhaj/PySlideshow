#!/usr/bin/env python

import sys

from PySide import QtCore
from PySide.QtGui import QApplication, QMainWindow, QFileDialog, QImage, QPixmap
from pathlib import Path
from random import randint

__version__ = '0.0.1'

from ui_slideshow import Ui_MainWindow
import qrc_slideshow

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        #button events
        self.btn_next.clicked.connect(self.next_image)
        self.btn_prev.clicked.connect(self.prev_image)

        #menu events
        self.action_exit.triggered.connect(self.close)
        self.action_open.triggered.connect(self.choose_dir)

        self.recursive = False
        self.image_paths = []
        self.i = -1


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Left:
            self.prev_image()
        elif e.key() == QtCore.Qt.Key_Right:
            self.next_image()


    def choose_dir(self):
        #TODO: show images in folders
        image_dir = QFileDialog.getExistingDirectory(self, self.tr("Choose directory"))
        self.i = -1

        if self.recursive:
            self.image_paths = [x for x in Path(image_dir).rglob("*") if x.suffix.lower() in ['.jpg', '.png', '.bmp']]
        else:
            self.image_paths = [x for x in Path(image_dir).glob("*") if x.suffix.lower() in ['.jpg', '.png', '.bmp']]

        #shuffle array
        for i in range(len(self.image_paths)-1, -1, -1):
            j = randint(0, i)
            self.image_paths[i], self.image_paths[j] = self.image_paths[j], self.image_paths[i]

        self.next_image()

    def update_image(self):
        image = QImage(str(self.image_paths[self.i]))

        if not image.isNull():
            lbl_size = (self.lbl_image.width(), self.lbl_image.height())
            img_size = (image.width(), image.height())
            ratio = (img_size[0] / lbl_size[0], img_size[1] / lbl_size[1])

            #if image width is greater than the label's and image is wider than tall
            if ratio[0] > 1 and ratio[0] > ratio[1]:
                #scale image to label's width
                image = image.scaledToWidth(lbl_size[0])

            #if height greater and image is taller than it is wide
            elif ratio[1] > 1 and ratio[1] > ratio[0]:
                #scale to label's height
                image = image.scaledToHeight(lbl_size[1])

            self.lbl_image.setPixmap(QPixmap.fromImage(image))

    def prev_image(self):
        if len(self.image_paths) > 1:
            self.i = (self.i - 1) % len(self.image_paths)
            self.update_image()

    def next_image(self):
        if len(self.image_paths) > 1:
            self.i = (self.i + 1) % len(self.image_paths)
            self.update_image()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()