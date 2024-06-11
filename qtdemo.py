# Nicholas Moreland
# 1001886051

from motion_detector import MotionDetector
import sys
import argparse
from PySide2 import QtCore, QtWidgets, QtGui
from skvideo.io import vread
from skimage.draw import rectangle_perimeter


class QtDemo(QtWidgets.QWidget):
    def __init__(self, frames):
        super().__init__()

        # Store frames
        self.frames = frames
        self.current_frame = 0

        # Configure buttons
        self.forward_button = QtWidgets.QPushButton("Forward 60 frames")
        self.backward_button = QtWidgets.QPushButton("Backward 60 frames")

        # Initialize the history
        self.history = []

        # Configure image label
        self.img_label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        h, w, c = self.frames[0].shape
        if c == 1:
            img = QtGui.QImage(
                self.frames[0], w, h, QtGui.QImage.Format_Grayscale8)
        else:
            img = QtGui.QImage(
                self.frames[0], w, h, QtGui.QImage.Format_RGB888)
        self.img_label.setPixmap(QtGui.QPixmap.fromImage(img))

        # Configure slider
        self.frame_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.frame_slider.setTickInterval(1)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(self.frames.shape[0]-1)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.img_label)
        self.layout.addWidget(self.forward_button)
        self.layout.addWidget(self.backward_button)
        self.layout.addWidget(self.frame_slider)

        # Connect functions
        self.forward_button.clicked.connect(self.on_click_forward)
        self.backward_button.clicked.connect(self.on_click_backward)
        self.frame_slider.sliderMoved.connect(self.on_move)

    @QtCore.Slot()
    def on_click_forward(self):
        # Initialize the collection of centers
        center_collection = []

        if self.current_frame == self.frames.shape[0]-1:
            return
        h, w, c = self.frames[self.current_frame].shape
        if c == 1:
            img = QtGui.QImage(
                self.frames[self.current_frame], w, h, QtGui.QImage.Format_Grayscale8)
        else:
            img = QtGui.QImage(
                self.frames[self.current_frame], w, h, QtGui.QImage.Format_RGB888)
        self.img_label.setPixmap(QtGui.QPixmap.fromImage(img))

        # Update frame
        center_collection = motion_detector.update_frame(self.current_frame)

        # Append to history
        self.history.append(center_collection)

        # Fast forward 60s into the next frame or to the end
        if self.current_frame + 60 > self.frames.shape[0]-1:
            self.current_frame = self.frames.shape[0]-1
        else:
            self.current_frame += 60
            print('Frame: ', end="")
            print(self.current_frame)

            # Loop through the history and draw the rectangles
            for i in range(len(self.history)):
                for j in range(len(self.history[i])):
                    # Get the center
                    center = (int(self.history[i][j][0]),
                              int(self.history[i][j][1]))

                    # Get the row and column
                    center_row = int(center[0])
                    center_col = int(center[1])

                    # Draw the rectangle
                    left = max(center_col - 10, 1)
                    right = min(center_col + 10, self.frames.shape[2]-1)
                    top = max(center_row - 10, 1)
                    bottom = min(center_row + 10, self.frames.shape[1]-1)

                    cords = rectangle_perimeter([top, left], [bottom, right])
                    self.frames[self.current_frame][cords] = (0, 0, 200)

    @QtCore.Slot()
    def on_click_backward(self):
        # Initialize the collection of centers
        center_collection = []

        if self.current_frame == self.frames.shape[0]-1:
            return
        h, w, c = self.frames[self.current_frame].shape
        if c == 1:
            img = QtGui.QImage(
                self.frames[self.current_frame], w, h, QtGui.QImage.Format_Grayscale8)
        else:
            img = QtGui.QImage(
                self.frames[self.current_frame], w, h, QtGui.QImage.Format_RGB888)
        self.img_label.setPixmap(QtGui.QPixmap.fromImage(img))

        # Clear history
        self.history = []

        # Update frame
        center_collection = motion_detector.update_frame(self.current_frame)

        # Append to history
        self.history.append(center_collection)

        # Backward 60s into the previous frame or to the start
        if self.current_frame - 60 < 0:
            self.current_frame = 0
        else:
            self.current_frame -= 60

            print('Frame: ', end="")
            print(self.current_frame)

            # Loop through the history and draw the rectangles
            for i in range(len(self.history)):
                for j in range(len(self.history[i])):
                    # Get the center
                    center = (int(self.history[i][j][0]),
                              int(self.history[i][j][1]))
                    # Get the row and column
                    center_row = int(center[0])
                    center_col = int(center[1])

                    # Draw the rectangle
                    left = max(center_col - 10, 1)
                    right = min(center_col + 10, self.frames.shape[2]-1)
                    top = max(center_row - 10, 1)
                    bottom = min(center_row + 10, self.frames.shape[1]-1)

                    cords = rectangle_perimeter([top, left], [bottom, right])
                    self.frames[self.current_frame][cords] = (0, 0, 200)

    @QtCore.Slot()
    def on_move(self, pos):
        self.current_frame = pos
        print('Frame: ', end="")
        print(self.current_frame)

        self.history.clear()
        h, w, c = self.frames[self.current_frame].shape
        if c == 1:
            img = QtGui.QImage(
                self.frames[self.current_frame], w, h, QtGui.QImage.Format_Grayscale8)
        else:
            img = QtGui.QImage(
                self.frames[self.current_frame], w, h, QtGui.QImage.Format_RGB888)
        self.img_label.setPixmap(QtGui.QPixmap.fromImage(img))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Demo for loading video with Qt5.")
    parser.add_argument("video_path", metavar='PATH_TO_VIDEO', type=str)
    parser.add_argument("--num_frames", metavar='n', type=int, default=-1)
    parser.add_argument("--grey", metavar='True/False',
                        type=str, default=False)
    args = parser.parse_args()

    num_frames = args.num_frames

    if num_frames > 0:
        frames = vread(args.video_path, num_frames=num_frames,
                       as_grey=args.grey)
    else:
        frames = vread(args.video_path, as_grey=args.grey)

    # Forming a MotionDetector object
    motion_detector = MotionDetector(frames, 0.1, 0.2, 0.1, 0.2, 2)
    app = QtWidgets.QApplication([])

    widget = QtDemo(frames)
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
