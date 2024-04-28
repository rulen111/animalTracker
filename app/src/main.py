import numpy as np
import pandas as pd

from app.src.analysis import roi_locate, get_roi_series, roi_transitions, preprocess_track, generate_summary
from app.src.tracker import Tracker, save_outputv
from app.src.video import Video
import cv2

vid = Video(fpath="test.avi")
vid.dsmpl = 0.5
vid.tr_range = (300, 1000)
vid.bg_ref[0] = "median"
points = [[279, 101], [1169, 114], [1164, 699], [1440, 707], [1440, 983], [287, 986]]
vid.generate_mask(points)
vid.make_bg()
vid.roi["start"] = [[581, 353], [721, 352], [718, 494], [575, 491]]
vid.roi["err"] = [[290, 55], [442, 56], [439, 207], [288, 204]]

# vid.save_state(f"{vid.fname}.pckl")

# cv2.imshow("bg", vid.bg_ref[1] / 255.)
# cv2.waitKey(0)
#
tracker = Tracker(params={"bg_ref": vid.bg_ref[1], "thresh": 99.5})

res = tracker.do_tracking(vid)
print(res.head(10))
res.to_csv("coords.csv", encoding='utf-8', index=False)
report = preprocess_track(res, vid.roi)
print(report.head(20))
# roi_locations = roi_locate(res, vid.roi)
# print(roi_locations.head(10))
# roi_series = get_roi_series(roi_locations)
# print(roi_series[:30])
# transitions = roi_transitions(roi_series)
# print(transitions[:30])
# transitions_labels = roi_transitions_labels(pd.concat([roi_series, transitions], axis=1))
# print(transitions_labels[:30])
# report = pd.concat([res, roi_locations, roi_series, transitions], axis=1)
# print(report.head(10))
report.to_csv("report.csv", encoding='utf-8', index=False)
summary = generate_summary({vid.fname: report}, list(vid.roi.keys()))
print(summary.head(20))
summary.to_csv("summary.csv", encoding='utf-8', index=False)
# save_outputv(vid)

# cv2.destroyAllWindows()
