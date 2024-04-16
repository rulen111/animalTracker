import cv2
import numpy as np
from tqdm import tqdm
import ntpath


class Video:
    def __init__(self, fpath):
        self.fpath = fpath
        self.folder = ntpath.dirname(fpath)
        self.fname = ntpath.basename(fpath)

        self.bg_fpath = ""
        self.dsmpl = 1.
        self.bg_ref = ["", None]

        cap = cv2.VideoCapture(fpath)
        self.frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = cap.get(cv2.CAP_PROP_FPS)
        self.shape = (int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                      int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        self.tr_range = [0, self.frame_cnt]

        self.tracked = False

        self.cropp = [0, 0, self.shape[0], self.shape[1]]
        self.mask = []
        self.roi = {}

        cap.release()

    def copy_params(self, other):
        pass

    def resizeframe(self, frame):
        frame_rs = cv2.resize(frame,
                              (
                                  int(frame.shape[1] * self.dsmpl),
                                  int(frame.shape[0] * self.dsmpl)
                              ),
                              cv2.INTER_AREA)
        return frame_rs

    def cropframe(self, frame):
        x = (self.cropp[0], self.cropp[2])
        y = (self.cropp[1], self.cropp[3])
        return frame[x[0]:x[1], y[0]:y[1]]

    def apply_mask(self, frame):
        frame_masked = cv2.bitwise_and(frame, frame, self.mask)
        return frame_masked

    def preprocess_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = self.cropframe(frame)
        if self.dsmpl < 1:
            frame = self.resizeframe(frame)
        if self.mask:
            frame = self.apply_mask(frame)
        return frame

    def make_bg(self, num_frames=50, bgfile=False):
        cap = cv2.VideoCapture(self.fpath) if not bgfile else cv2.VideoCapture(self.bg_fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        ret, frame = cap.read()
        frame = self.preprocess_frame(frame)

        h, w = frame.shape[0], frame.shape[1]
        frames = np.linspace(start=self.tr_range[0], stop=self.tr_range[1], num=num_frames)

        collection = np.zeros((num_frames, h, w))
        print(f"Computing background reference image")
        for (idx, framenum) in enumerate(tqdm(frames)):
            grabbed = False
            while not grabbed:
                cap.set(cv2.CAP_PROP_POS_FRAMES, framenum)
                ret, frame = cap.read()
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    if self.dsmpl < 1:
                        gray = self.resizeframe(gray)
                    gray = self.cropframe(gray)

                    collection[idx, :, :] = gray
                    grabbed = True

                else:
                    framenum = np.random.randint(self.tr_range[0], self.tr_range[1], 1)[0]

        cap.release()

        if self.bg_ref[0] == "median":
            self.bg_ref[1] = np.median(collection, axis=0)
        elif self.bg_ref[0] == "mean":
            self.bg_ref[1] = np.mean(collection, axis=0)
        elif self.bg_ref[0] == "max":
            self.bg_ref[1] = np.max(collection, axis=0)
        elif self.bg_ref[0] == "min":
            self.bg_ref[1] = np.min(collection, axis=0)
        else:
            # TODO: Add handler
            pass
