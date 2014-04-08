#!/usr/bin/env python

import sys
from pathlib import Path

from random import randint

from PySide import QtCore
from PySide.QtGui import QApplication, QMainWindow, QFileDialog, QImage, QPixmap, QIcon, QInputDialog, QMessageBox

__version__ = '1.0.0'

from ui_slideshow import Ui_MainWindow
import qrc_slideshow

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        #self.showFullScreen()

        #button events
        self.btn_next.clicked.connect(self.next_image)
        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_play.clicked.connect(self.slideshow)
        self.btn_delete.clicked.connect(self.delete_image)

        #menu events
        self.action_exit.triggered.connect(self.close)
        self.action_open.triggered.connect(self.choose_dir)
        self.action_speed_fast.triggered.connect(lambda: self.slideshow_speed(0))
        self.action_speed_medium.triggered.connect(lambda: self.slideshow_speed(1))
        self.action_speed_slow.triggered.connect(lambda: self.slideshow_speed(2))
        self.action_speed_custom.triggered.connect(lambda: self.slideshow_speed(3))

        self.image_paths = []
        self.i = -1
        self.playing = False

        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.next_image)
        self.slideshow_speed(1)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Left:
            self.prev_image()
        elif e.key() == QtCore.Qt.Key_Right:
            self.next_image()
        elif e.key() == QtCore.Qt.Key_Space:
            self.slideshow()
        elif e.key() == QtCore.Qt.Key_Delete:
            self.delete_image()


    def choose_dir(self):
        #todo: show images in folders
        image_dir = QFileDialog.getExistingDirectory(self, self.tr("Choose directory"))
        self.i = -1

        if self.action_recursive.isChecked():
            self.image_paths = [x for x in Path(image_dir).rglob("*") if x.suffix.lower() in ['.jpg', '.png', '.bmp']]
        else:
            self.image_paths = [x for x in Path(image_dir).glob("*") if x.suffix.lower() in ['.jpg', '.png', '.bmp']]

        if len(self.image_paths) > 0:
            self.btn_next.setEnabled(True)
            self.btn_prev.setEnabled(True)
            self.btn_play.setEnabled(True)
            self.btn_delete.setEnabled(True)

            #shuffle array
            for i in range(len(self.image_paths)-1, -1, -1):
                j = randint(0, i)
                self.image_paths[i], self.image_paths[j] = self.image_paths[j], self.image_paths[i]

            self.next_image()
        else:
            self.btn_next.setEnabled(False)
            self.btn_prev.setEnabled(False)
            self.btn_play.setEnabled(False)
            self.btn_delete.setEnabled(False)

            QMessageBox.information(self, "No Images", "No images were found in " + image_dir)

    def update_image(self):
        self.status_bar.showMessage(str(self.image_paths[self.i]))
        image = QImage(str(self.image_paths[self.i]))

        if not image.isNull():
            lbl_size = (self.lbl_image.width(), self.lbl_image.height())
            img_size = (image.width(), image.height())
            ratio = (img_size[0] / lbl_size[0], img_size[1] / lbl_size[1])

            #if image width is greater than the label's and image is wider than tall
            if ratio[0] > 1 and ratio[0] > ratio[1]:
                #scale image to label's width
                image = image.scaledToWidth(lbl_size[0], QtCore.Qt.SmoothTransformation)

            #if height greater and image is taller than it is wide
            elif ratio[1] > 1 and ratio[1] > ratio[0]:
                #scale to label's height
                image = image.scaledToHeight(lbl_size[1], QtCore.Qt.SmoothTransformation)

            self.lbl_image.setPixmap(QPixmap.fromImage(image))

    def prev_image(self):
        if len(self.image_paths) > 1:
            self.i = (self.i - 1) % len(self.image_paths)
            self.update_image()

    def next_image(self):
        if len(self.image_paths) > 1:
            self.i = (self.i + 1) % len(self.image_paths)
            self.update_image()

    def delete_image(self):
        if self.i > -1 and len(self.image_paths) > 0:
            Path.unlink(self.image_paths[self.i])
            self.image_paths.pop(self.i)
            self.next_image()


    def slideshow(self):
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/images/media-playback-start.png"), QIcon.Normal, QIcon.Off)
        if self.playing:
            icon.addPixmap(QPixmap(":/icons/images/media-playback-start.png"), QIcon.Normal, QIcon.Off)
            self.btn_play.setIcon(icon)
            self.playing = False
            self.timer.stop()
        else:
            icon.addPixmap(QPixmap(":/icons/images/media-playback-pause.png"), QIcon.Normal, QIcon.Off)
            self.btn_play.setIcon(icon)
            self.playing = True
            self.timer.start()

    def slideshow_speed(self, speed):
        """
        Set the slideshow interval based on 'sender' where
        - 0 == fast (2s)
        - 1 == medium (5s)
        - 2 == slow (10s)
        - 3 == custom (1-60s)
        """
        intervals = [2000, 5000, 10000] #fast, medium, slow, custom slideshow intervals (milliseconds)

        self.action_speed_fast.setChecked(speed == 0)
        self.action_speed_medium.setChecked(speed == 1)
        self.action_speed_slow.setChecked(speed == 2)
        self.action_speed_custom.setChecked(speed >= 3)

        if 0 <= speed < 3:
            self.timer.setInterval(intervals[speed])
        else:
            custom_speed, ok = QInputDialog.getInt(self, 'Custom Speed', 'Enter slideshow speed (1-60 seconds):', 1, 1, 60)

            custom_speed *= 1000 #convert to seconds

            if ok:
                self.timer.setInterval(custom_speed)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()