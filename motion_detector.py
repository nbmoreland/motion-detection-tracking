# Nicholas Moreland
# 1001886051

import numpy as np
from skimage.color import rgb2gray
from skimage.measure import label, regionprops
from skimage.morphology import dilation
from kalman_filter import KalmanFilter


class MotionDetector(object):
    def __init__(self, frames, alpha, tau, delta, s, N):
        idx = 2

        # Initialize the Kalman Filter
        self.KF = KalmanFilter(1, 1, 1, 1, 0.1, 0.1)

        # Initialize the parameters
        self.frames = frames
        self.alpha = alpha
        self.tau = tau
        self.delta = delta
        self.s = s
        self.N = N

        # Initialize the frames
        self.ppframe = rgb2gray(frames[idx-2])
        self.pframe = rgb2gray(frames[idx-1])
        self.cframe = rgb2gray(frames[idx])

    def update_frame(self, current_frame):
        # Update the frames
        self.ppframe = rgb2gray(self.frames[current_frame-2])
        self.pframe = rgb2gray(self.frames[current_frame-1])
        self.cframe = rgb2gray(self.frames[current_frame])

        # Compute the difference
        diff1 = np.abs(self.cframe - self.pframe)
        diff2 = np.abs(self.pframe - self.ppframe)

        # Compute the motion frame
        motion_frame = np.minimum(diff1, diff2)
        thresh_frame = motion_frame > self.tau
        dilated_frame = dilation(thresh_frame, np.ones((9, 9)))
        label_frame = label(dilated_frame)
        regions = regionprops(label_frame)

        # Initialize the collection of centers
        center_collection = []

        # Loop over the regions
        for region in regions:
            # Compute the area
            prediction = self.KF.predict()

            # Update the Kalman Filter
            prediction = (self.KF.update(region.centroid)).tolist()

            # Extract the x and y
            x = int(prediction[0][0])
            y = int(prediction[0][1])

            # Add x and y to the collection
            center_collection.append([x, y])

        # Return the collection of centers
        return center_collection
