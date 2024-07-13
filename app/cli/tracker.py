import pickle

from scipy.ndimage import center_of_mass

from app.cli.preprocessing import Preprocessing
from app.cli.video import Video
import cv2
import numpy as np
from tqdm import tqdm
import pandas as pd
from datetime import datetime


def calc_dist(x, y, xprev, yprev):
    return np.sqrt((y - yprev) ** 2 + (x - xprev) ** 2)


# class Tracker(object):
#     def __init__(self, method="diff", params=None):
#         self.method = method
#         self.params = params if params else {}
#
#     def save_state(self, fpath):
#         state = self.__dict__
#         print(state)
#         with open(fpath, 'wb') as f:
#             pickle.dump(state, f)
#
#     def load_state(self, fpath):
#         with open(fpath, 'rb') as f:
#             self.__dict__ = pickle.load(f)
#
#     def locate_diff(self, frame):
#         dif = np.absolute(frame - self.params["bg_ref"]).astype('int16')
#
#         dif[dif < np.percentile(dif, self.params["thresh"])] = 0
#
#         com = center_of_mass(dif)
#
#         return dif, com, frame
#
#     def do_tracking(self, vid):
#         cap = cv2.VideoCapture(vid.fpath)
#         cap.set(cv2.CAP_PROP_POS_FRAMES, vid.tr_range[0])
#
#         xvec = np.zeros(vid.tr_range[1] - vid.tr_range[0])
#         yvec = np.zeros(vid.tr_range[1] - vid.tr_range[0])
#         dvec = np.zeros(vid.tr_range[1] - vid.tr_range[0])
#
#         # tvec = np.zeros(vid.tr_range[1] - vid.tr_range[0], dtype='<U9')
#         tvec = np.zeros(vid.tr_range[1] - vid.tr_range[0])
#
#         print(f"Starting tracking")
#         for f in tqdm(range(len(dvec))):
#             ret, frame = cap.read()
#             dif, com = None, None
#             if ret:
#                 frame = vid.preprocess_frame(frame)
#                 if self.method == "diff":
#                     dif, com, frame = self.locate_diff(frame)
#
#                 xvec[f] = com[1]
#                 yvec[f] = com[0]
#
#                 msec_float = cap.get(cv2.CAP_PROP_POS_MSEC)
#                 # minutes = f"{int(msec_float / 1000.0) // 60:02d}"
#                 # seconds = f"{int(msec_float / 1000.0) % 60:02d}"
#                 # # milliseconds = f"{str(round(msec_float, 3)).split('.')[-1]:3d}"
#                 # milliseconds = f"{int(msec_float % 1000.0):03d}"
#                 # timestamp = ":".join([minutes, seconds, milliseconds])
#                 # tvec[f] = timestamp
#                 tvec[f] = msec_float
#                 if f > 0:
#                     # dvec[f] = np.sqrt((yvec[f] - yvec[f - 1]) ** 2 + (xvec[f] - xvec[f - 1]) ** 2)
#                     dvec[f] = calc_dist(xvec[f], yvec[f], xvec[f - 1], yvec[f - 1])
#             else:
#                 f = f - 1
#                 xvec = xvec[:f]  # Amend length of X vector
#                 yvec = yvec[:f]  # Amend length of Y vector
#                 dvec = dvec[:f]  # Amend length of D vector
#                 tvec = tvec[:f]  # Amend length of D vector
#                 break
#
#         cap.release()
#         print('total frames processed: {f}\n'.format(f=len(dvec)))
#         # vid.track = [xvec, yvec, dvec]
#
#         # create pandas dataframe
#         df = pd.DataFrame(
#             {'X': xvec,
#              'Y': yvec,
#              'Distance_px': dvec,
#              'Timestamp_msec': tvec
#              })
#
#         vid.track = df
#
#         return df


def save_outputv(vid: Video, preproc: Preprocessing):
    cap = cv2.VideoCapture(vid.fpath)  # set file
    cap.set(cv2.CAP_PROP_POS_FRAMES, preproc.tracking_interval[0])  # set starting frame

    ret, frame = cap.read()  # read frame
    frame = preproc.preprocess_frame(frame)

    height, width = int(frame.shape[0]), int(frame.shape[1])

    fourcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
    writer = cv2.VideoWriter(vid.folder + 'test_out.avi',
                             fourcc, 20,
                             (width, height),
                             isColor=False)

    cap.set(cv2.CAP_PROP_POS_FRAMES, preproc.tracking_interval[0])

    for f in tqdm(range(preproc.tracking_interval[1] - preproc.tracking_interval[0])):
        ret, frame = cap.read()
        if ret:
            frame = preproc.preprocess_frame(frame)

            # position = (int(vid.track[0][f]), int(vid.track[1][f]))
            position = (int(vid.track.iloc[f, 0]), int(vid.track.iloc[f, 1]))
            cv2.drawMarker(img=frame, position=position, color=255)
            writer.write(frame)
        else:
            print('warning. failed to get video frame')

    writer.release()
