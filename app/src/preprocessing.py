import cv2
import numpy as np


class Preprocessing(object):

    def __init__(self, *args, **kwargs):
        self.resolution = kwargs.get("resolution", 1.)
        self.tracking_interval = kwargs.get("tracking_interval", None)
        self.mask = kwargs.get("mask", np.array([]))

    def resize_frame(self, frame):
        frame_rs = cv2.resize(frame,
                              (
                                  int(frame.shape[1] * self.resolution),
                                  int(frame.shape[0] * self.resolution)
                              ),
                              cv2.INTER_AREA)
        return frame_rs

    def apply_mask(self, frame):
        frame_masked = cv2.bitwise_and(frame, self.mask)
        return frame_masked

    def preprocess_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.mask.any():
            frame = self.apply_mask(frame)
        if self.resolution < 1:
            frame = self.resize_frame(frame)

        return frame

    def generate_mask(self, points, shape):
        points = np.array(points)
        size1 = shape[0]
        size2 = shape[1]

        canvas = np.zeros((size1, size2), dtype=np.uint8)
        mask = cv2.fillPoly(canvas, [points], 255)

        self.mask = mask
