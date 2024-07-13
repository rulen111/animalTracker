import cv2
import numpy as np
import pandas as pd
from scipy.ndimage import center_of_mass
from tqdm import tqdm

from app.cli.preprocessing import Preprocessing
from app.cli.video import Video


def calc_dist(x, y, xprev, yprev):
    return np.sqrt((y - yprev) ** 2 + (x - xprev) ** 2)


class Tracking(object):

    def __init__(self, *args, **kwargs):
        self.method = kwargs.get("method", "diff")
        self.bg_method = kwargs.get("bg_method", "median")
        self.threshold = kwargs.get("threshold", 99.5)
        self.bg_fpath = kwargs.get("bg_fpath", "")
        self.bg_img = kwargs.get("bg_img", np.array([]))

    def make_bg(self, vid: Video, preproc: Preprocessing, num_frames=50):
        cap = cv2.VideoCapture(vid.fpath) if not self.bg_fpath else cv2.VideoCapture(self.bg_fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        ret, frame = cap.read()
        frame = preproc.preprocess_frame(frame)

        h, w = frame.shape[0], frame.shape[1]
        frames = np.linspace(start=preproc.tracking_interval[0], stop=preproc.tracking_interval[1], num=num_frames)

        collection = np.zeros((num_frames, h, w), dtype=np.uint8)
        print(f"Computing background reference image")
        for (idx, framenum) in enumerate(tqdm(frames)):
            grabbed = False
            while not grabbed:
                cap.set(cv2.CAP_PROP_POS_FRAMES, framenum)
                ret, frame = cap.read()
                if ret:
                    frame = preproc.preprocess_frame(frame)

                    collection[idx, :, :] = frame
                    grabbed = True

                else:
                    framenum = np.random.randint(preproc.tracking_interval[0], preproc.tracking_interval[1], 1)[0]

        cap.release()

        if self.bg_method == "median":
            self.bg_img = np.median(collection, axis=0)
        elif self.bg_method == "mean":
            self.bg_img = np.mean(collection, axis=0)
        elif self.bg_method == "max":
            self.bg_img = np.max(collection, axis=0)
        elif self.bg_method == "min":
            self.bg_img = np.min(collection, axis=0)
        else:
            # TODO: Add handler
            pass

    def locate_diff(self, frame):
        dif = np.absolute(frame - self.bg_img).astype('int16')

        dif[dif < np.percentile(dif, self.threshold)] = 0

        com = center_of_mass(dif)

        return dif, com, frame

    def do_tracking(self, vid: Video, preproc: Preprocessing):
        cap = cv2.VideoCapture(vid.fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, preproc.tracking_interval[0])

        xvec = np.zeros(preproc.tracking_interval[1] - preproc.tracking_interval[0])
        yvec = np.zeros(preproc.tracking_interval[1] - preproc.tracking_interval[0])
        dvec = np.zeros(preproc.tracking_interval[1] - preproc.tracking_interval[0])

        # tvec = np.zeros(vid.tr_range[1] - vid.tr_range[0], dtype='<U9')
        tvec = np.zeros(preproc.tracking_interval[1] - preproc.tracking_interval[0])

        print(f"Starting tracking")
        for f in tqdm(range(len(dvec))):
            ret, frame = cap.read()
            dif, com = None, None
            if ret:
                frame = preproc.preprocess_frame(frame)
                if self.method == "diff":
                    dif, com, frame = self.locate_diff(frame)

                xvec[f] = com[1]
                yvec[f] = com[0]

                msec_float = cap.get(cv2.CAP_PROP_POS_MSEC)
                # minutes = f"{int(msec_float / 1000.0) // 60:02d}"
                # seconds = f"{int(msec_float / 1000.0) % 60:02d}"
                # # milliseconds = f"{str(round(msec_float, 3)).split('.')[-1]:3d}"
                # milliseconds = f"{int(msec_float % 1000.0):03d}"
                # timestamp = ":".join([minutes, seconds, milliseconds])
                # tvec[f] = timestamp
                tvec[f] = msec_float
                if f > 0:
                    # dvec[f] = np.sqrt((yvec[f] - yvec[f - 1]) ** 2 + (xvec[f] - xvec[f - 1]) ** 2)
                    dvec[f] = calc_dist(xvec[f], yvec[f], xvec[f - 1], yvec[f - 1])
            else:
                f = f - 1
                xvec = xvec[:f]  # Amend length of X vector
                yvec = yvec[:f]  # Amend length of Y vector
                dvec = dvec[:f]  # Amend length of D vector
                tvec = tvec[:f]  # Amend length of D vector
                break

        cap.release()
        print('total frames processed: {f}\n'.format(f=len(dvec)))
        # vid.track = [xvec, yvec, dvec]

        # create pandas dataframe
        df = pd.DataFrame(
            {'X': xvec,
             'Y': yvec,
             'Distance_px': dvec,
             'Timestamp_msec': tvec
             })

        vid.track = df

        return df
