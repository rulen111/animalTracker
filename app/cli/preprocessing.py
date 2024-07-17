import pathlib
import pickle

import cv2
import numpy as np

import shelve


class Preprocessing(object):

    def __init__(self, *args, **kwargs):
        self.resolution = kwargs.get("resolution", 1.)
        self.tracking_interval = kwargs.get("tracking_interval", None)
        self.mask = kwargs.get("mask", np.array([]))

    def save(self, fpath):
        # with shelve.open(fpath) as db:
        #     db["Preprocessing"] = {
        #         "resolution": self.resolution,
        #         "tracking_interval": self.tracking_interval,
        #         "mask": self.mask,
        #     }

        if pathlib.Path(fpath).exists():
            with open(fpath, "rb") as f:
                temp = pickle.load(f)
        else:
            temp = {}

        temp.update({
            "Preprocessing": {
                "resolution": self.resolution,
                "tracking_interval": self.tracking_interval,
                "mask": self.mask,
            }
        })

        with open(fpath, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, fpath):
        # with shelve.open(fpath) as db:
        #     if "Preprocessing" in db:
        #         self.__dict__.update(db["Preprocessing"])

        if pathlib.Path(fpath).exists():
            with open(fpath, "rb") as f:
                entries = pickle.load(f)
        else:
            return

        if "Preprocessing" in entries:
            self.__dict__.update(entries["Preprocessing"])

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
