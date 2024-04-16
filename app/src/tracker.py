from scipy.ndimage import center_of_mass
from app.src.video import Video
import cv2
import numpy as np
from tqdm import tqdm
import pandas as pd


class Tracker:
    def __init__(self, method="diff", params=None):
        self.method = method
        self.params = params

    def locate_diff(self, frame):
        dif = np.absolute(frame - self.params["bg_ref"]).astype('int16')

        dif[dif < np.percentile(dif, self.params["thresh"])] = 0

        com = center_of_mass(dif)

        return dif, com, frame

    def do_tracking(self, vid, track=None):
        cap = cv2.VideoCapture(vid.fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, vid.tr_range[0])

        xvec = np.zeros(vid.tr_range[1] - vid.tr_range[0])
        yvec = np.zeros(vid.tr_range[1] - vid.tr_range[0])
        dvec = np.zeros(vid.tr_range[1] - vid.tr_range[0])

        print(f"Starting tracking")
        for f in tqdm(range(len(dvec))):
            ret, frame = cap.read()
            dif, com = None, None
            if ret:
                frame = vid.preprocess_frame(frame)
                if self.method == "diff":
                    dif, com, frame = self.locate_diff(frame)

                xvec[f] = com[1]
                yvec[f] = com[0]
                if f > 0:
                    dvec[f] = np.sqrt((yvec[f] - yvec[f - 1]) ** 2 + (xvec[f] - xvec[f - 1]) ** 2)
            else:
                f = f - 1
                xvec = xvec[:f]  # Amend length of X vector
                yvec = yvec[:f]  # Amend length of Y vector
                dvec = dvec[:f]  # Amend length of D vector
                break

        cap.release()
        print('total frames processed: {f}\n'.format(f=len(dvec)))

        # create pandas dataframe
        df = pd.DataFrame(
            {'Video': vid.fname,
             'Start_Frame': vid.tr_range[0],
             'Frame': np.arange(len(dvec)) + vid.tr_range[0],
             'X': xvec,
             'Y': yvec,
             'Distance_px': dvec
             })

        return df


def save_outputv(vid: Video, df):
    cap = cv2.VideoCapture(vid.fpath)  # set file
    cap.set(cv2.CAP_PROP_POS_FRAMES, vid.tr_range[0])  # set starting frame

    ret, frame = cap.read()  # read frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if vid.dsmpl < 1:
        frame = vid.resizeframe(frame)
    frame = vid.cropframe(frame)

    height, width = int(frame.shape[0]), int(frame.shape[1])

    fourcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
    writer = cv2.VideoWriter(vid.folder + 'test_out.avi',
                             fourcc, 20,
                             (width, height),
                             isColor=False)

    cap.set(cv2.CAP_PROP_POS_FRAMES, vid.tr_range[0])

    for f in tqdm(range(vid.tr_range[1] - vid.tr_range[0])):
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if vid.dsmpl < 1:
                frame = vid.resizeframe(frame)
            frame = vid.cropframe(frame)

            position = (int(df['X'][f]), int(df['Y'][f]))
            cv2.drawMarker(img=frame, position=position, color=255)
            writer.write(frame)
        else:
            print('warning. failed to get video frame')

    writer.release()
