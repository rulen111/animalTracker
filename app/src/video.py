import cv2
import numpy as np
from tqdm import tqdm
import ntpath
import pickle


# TODO: Add decorator for saving class state

class Video(object):
    def __init__(self, fpath=None):
        self.fpath = None
        self.folder = None
        self.fname = None

        self.bg_fpath = ""
        self.dsmpl = 1.
        self.bg_ref = ["median", None]

        self.frame_cnt = None
        self.frame_rate = None
        self.shape = None
        self.tr_range = None

        self.tracked = False

        self.cropp = None
        self.mask = np.array([])

        self.roi = {}

        if fpath:
            self.load_video(fpath)

    def save_state(self, fpath):
        state = self.__dict__
        with open(fpath, 'wb') as f:
            pickle.dump(state, f)

    def load_state(self, fpath):
        with open(fpath, 'rb') as f:
            self.__dict__ = pickle.load(f)

    def load_video(self, fpath):
        cap = cv2.VideoCapture(fpath)

        self.fpath = fpath
        self.folder = ntpath.dirname(fpath)
        self.fname = ntpath.basename(fpath)

        self.frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = cap.get(cv2.CAP_PROP_FPS)
        self.shape = (int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                      int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        self.tr_range = [0, self.frame_cnt]

        self.cropp = [0, 0, self.shape[0], self.shape[1]]

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
        frame_masked = cv2.bitwise_and(frame, self.mask)
        return frame_masked

    def preprocess_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # frame = self.cropframe(frame)
        if self.mask.any():
            frame = self.apply_mask(frame)
        if self.dsmpl < 1:
            frame = self.resizeframe(frame)
        return frame

    def make_bg(self, num_frames=50, bgfile=False):
        cap = cv2.VideoCapture(self.fpath) if not bgfile else cv2.VideoCapture(self.bg_fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        ret, frame = cap.read()
        frame = self.preprocess_frame(frame)

        h, w = frame.shape[0], frame.shape[1]
        frames = np.linspace(start=self.tr_range[0], stop=self.tr_range[1], num=num_frames)

        collection = np.zeros((num_frames, h, w), dtype=np.uint8)
        print(f"Computing background reference image")
        for (idx, framenum) in enumerate(tqdm(frames)):
            grabbed = False
            while not grabbed:
                cap.set(cv2.CAP_PROP_POS_FRAMES, framenum)
                ret, frame = cap.read()
                if ret:
                    frame = self.preprocess_frame(frame)

                    collection[idx, :, :] = frame
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

    def generate_mask(self, points):
        points = np.array(points)
        # size1 = int((self.cropp[2] - self.cropp[0]) * self.dsmpl)
        # size2 = int((self.cropp[3] - self.cropp[1]) * self.dsmpl)
        size1 = self.shape[0]
        size2 = self.shape[1]

        canvas = np.zeros((size1, size2), dtype=np.uint8)
        mask = cv2.fillPoly(canvas, [points], (255, 255, 255))
        # mask = cv2.fillPoly(canvas, [points], 1)
        self.mask = mask
