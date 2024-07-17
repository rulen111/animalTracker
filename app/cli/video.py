import pathlib
import shelve

import cv2
import numpy as np
from tqdm import tqdm
import ntpath
import pickle


# TODO: Add decorator for saving class state

class Video(object):
    def __init__(self, *args, **kwargs):
        self.fpath = kwargs.get("fpath", None)
        self.folder = kwargs.get("folder", None)
        self.fname = kwargs.get("fname", None)

        # self.bg_fpath = kwargs.get("bg_fpath", "")
        # self.dsmpl = kwargs.get("dsmpl", 1.)
        # self.bg_ref = kwargs.get("bg_ref", ["median", None])

        self.frame_cnt = kwargs.get("frame_cnt", None)
        self.frame_rate = kwargs.get("frame_rate", None)
        self.shape = kwargs.get("shape", None)
        # self.tr_range = kwargs.get("tr_range", None)

        self.tracked = kwargs.get("tracked", False)
        self.track = kwargs.get("track", np.array([]))

        # self.mask = kwargs.get("mask", np.array([]))

        # self.roi = kwargs.get("roi", {})

        if self.fpath and not self.fname:
            try:
                self.load_video()
            except Exception as e:
                print(e)

    # def save_state(self, fpath):
    #     state = self.__dict__
    #     with open(fpath, 'wb') as f:
    #         pickle.dump(state, f)
    #
    # def load_state(self, fpath):
    #     with open(fpath, 'rb') as f:
    #         self.__dict__ = pickle.load(f)

    def save(self, fpath):
        # with shelve.open(fpath) as db:
        #     db["Video"] = {
        #         "fpath": self.fpath,
        #         "tracked": self.tracked,
        #         "track": self.track,
        #     }
        if pathlib.Path(fpath).exists():
            with open(fpath, "rb") as f:
                temp = pickle.load(f)
        else:
            temp = {}

        temp.update({
            "Video": {
                "fpath": self.fpath,
                "tracked": self.tracked,
                "track": self.track,
            }
        })

        with open(fpath, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, fpath):
        # with shelve.open(fpath) as db:
        #     if "Video" in db:
        #         self.__dict__.update(db["Video"])
        #         self.load_video()

        if pathlib.Path(fpath).exists():
            with open(fpath, "rb") as f:
                entries = pickle.load(f)
        else:
            return

        if "Video" in entries:
            self.__dict__.update(entries["Video"])
            self.load_video()

    def load_video(self):
        cap = cv2.VideoCapture(self.fpath)

        self.folder = ntpath.dirname(self.fpath)
        self.fname = ntpath.basename(self.fpath)

        self.frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = cap.get(cv2.CAP_PROP_FPS)
        self.shape = (int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                      int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        # self.tr_range = [0, self.frame_cnt]

        cap.release()

    def copy_params(self, other):
        pass
