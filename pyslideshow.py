#!/usr/bin/env python
"""
PySlideshow - A simple image slideshow viewer written in Python using PySide.
"""
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

        #button events
        self.btn_next.clicked.connect(self.next_image)
        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_play.clicked.connect(self.toggle_slideshow)
        self.btn_delete.clicked.connect(self.delete_image)

        #menu events
        self.action_exit.triggered.connect(self.close)
        self.action_open.triggered.connect(self.choose_dir)
        self.action_fullscreen.triggered.connect(self.toggle_fullscreen)
        self.action_speed_fast.triggered.connect(lambda: self.set_slideshow_speed(0))
        self.action_speed_medium.triggered.connect(lambda: self.set_slideshow_speed(1))
        self.action_speed_slow.triggered.connect(lambda: self.set_slideshow_speed(2))
        self.action_speed_custom.triggered.connect(lambda: self.set_slideshow_speed(3))

        self.image_paths = [] #list of images in the chosen directory
        self.i = -1 #index of current image in image_paths
        self.is_playing = False #slideshow playing?
        self.is_fullscreen = False #window fullscreen?

        #slideshow timer
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.next_image)
        self.set_slideshow_speed(1)

        #window properties
        self.window_palette = self.palette()
        self.is_maximized = self.isMaximized()
        self.window_dimensions = self.geometry()
        self.image_dimensions = (self.lbl_image.width(), self.lbl_image.height())

    def keyPressEvent(self, e):
        """Handle different keyboard shortcuts."""
        if e.key() == QtCore.Qt.Key_Left:
            self.prev_image()
        elif e.key() == QtCore.Qt.Key_Right:
            self.next_image()
        elif e.key() == QtCore.Qt.Key_Space:
            self.toggle_slideshow()
        elif e.key() == QtCore.Qt.Key_Delete:
            self.delete_image()
        elif e.key() == QtCore.Qt.Key_F11:
            self.toggle_fullscreen()
        elif e.key() == QtCore.Qt.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()

    def choose_dir(self):
        """Open file dialog to choose images directory."""
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
            for i in range(len(self.image_paths) - 1, -1, -1):
                j = randint(0, i)
                self.image_paths[i], self.image_paths[j] = self.image_paths[j], self.image_paths[i]

            self.next_image()
        else:
            self.btn_next.setEnabled(False)
            self.btn_prev.setEnabled(False)
            self.btn_play.setEnabled(False)
            self.btn_delete.setEnabled(False)

            QMessageBox.information(self, "No Images",
                                    "No images were found in '" + image_dir + "'. Choose another directory.")

    def update_image(self, size=None):
        """
        Display image at current index.

        Args:
            size (w,h): If provided, image scaled to this size. Otherwise, scaled to window size.
        """
        self.status_bar.showMessage(
            str(self.image_paths[self.i]) + "    " + str(self.i + 1) + " of " + str(len(self.image_paths) + 1))
        image = QImage(str(self.image_paths[self.i]))

        if not image.isNull():
            if size is None:
                lbl_size = (self.lbl_image.width(), self.lbl_image.height())
            else:
                lbl_size = size

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
        """Display previous image."""
        if len(self.image_paths) > 1:
            self.i = (self.i - 1) % len(self.image_paths)
            self.update_image()

    def next_image(self):
        """Display next image."""
        if len(self.image_paths) > 1:
            self.i = (self.i + 1) % len(self.image_paths)
            self.update_image()

    def delete_image(self):
        """Delete current image from filesystem."""
        if len(self.image_paths) > 0:
            Path.unlink(self.image_paths[self.i])
            self.image_paths.pop(self.i)
            self.i -= 1
            self.next_image()


    def toggle_slideshow(self):
        """Play or pauses the slideshow."""
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/images/media-playback-start.png"), QIcon.Normal, QIcon.Off)
        if self.is_playing:
            icon.addPixmap(QPixmap(":/icons/images/media-playback-start.png"), QIcon.Normal, QIcon.Off)
            self.btn_play.setIcon(icon)
            self.is_playing = False
            self.timer.stop()
        else:
            icon.addPixmap(QPixmap(":/icons/images/media-playback-pause.png"), QIcon.Normal, QIcon.Off)
            self.btn_play.setIcon(icon)
            self.is_playing = True
            self.timer.start()


    def toggle_fullscreen(self):
        """Toggle the fullscreen state of the main window."""
        if not self.is_fullscreen:
            if len(self.image_paths) < 1: #no point going fullscreen if no images loaded
                QMessageBox.information(self, "Error", "Open a directory with images before entering fullscreen mode.")
                self.action_fullscreen.setChecked(False)
                return
            else:
                #save window properties so window can be restored to current state when exiting fullscreen
                self.window_dimensions = self.geometry()
                self.is_maximized = self.isMaximized()
                self.image_dimensions = (self.lbl_image.width(), self.lbl_image.height())

                #set fullscreen on
                self.showFullScreen()
                self.is_fullscreen = True

                #set window background to black
                p = self.palette()
                p.setColor(self.backgroundRole(), QtCore.Qt.black)
                self.setPalette(p)
        else:
            #in fullscreen mode, images are scaled to fullscreen dimensions which prevents the window from returning
            #to original size when original size is smaller than fullscreen dimensions. therefore, resize image to
            # original dimensions before exiting fullscreen
            self.update_image(self.image_dimensions)

            #change window background back to default
            self.setPalette(self.window_palette)

            #set fullscreen off
            self.is_fullscreen = False
            if self.is_maximized:
                #if window was maximised before entering fullscreen, maximise it again
                self.showMaximized()
            else:
                #otherwise, retore to its old dimensions
                self.showNormal()
                self.setGeometry(self.window_dimensions)

        self.menubar.setVisible(not self.is_fullscreen)
        self.btn_prev.setFlat(self.is_fullscreen)
        self.btn_play.setFlat(self.is_fullscreen)
        self.btn_next.setFlat(self.is_fullscreen)
        self.btn_delete.setFlat(self.is_fullscreen)


    def set_slideshow_speed(self, speed):
        """
        Set the interval between each image based on 'speed'

        Args:
            speed: 0 = fast
                   1 == medium (5s)
                   2 == slow (10s)
                   3 == custom (1-60s)
        """
        intervals = [2000, 5000, 10000] #fast, medium, slow slideshow intervals (milliseconds)

        #check the appropriate menu item
        self.action_speed_fast.setChecked(speed == 0)
        self.action_speed_medium.setChecked(speed == 1)
        self.action_speed_slow.setChecked(speed == 2)
        self.action_speed_custom.setChecked(speed >= 3)

        if 0 <= speed < 3:
            self.timer.setInterval(intervals[speed])
        else:
            custom_speed, ok = QInputDialog.getInt(self, 'Custom Speed', 'Enter slideshow speed (1-60 seconds):',
                                                   1, 1, 60)
            custom_speed *= 1000 #convert to seconds
            if ok:
                self.timer.setInterval(custom_speed)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()