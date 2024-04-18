import numpy as np

from app.src.tracker import Tracker, save_outputv
from app.src.video import Video
import cv2

vid = Video("test.avi")
vid.dsmpl = 0.5
vid.tr_range = (300, 1000)
vid.bg_ref[0] = "median"
points = [[279, 101], [1169, 114], [1164, 699], [1440, 707], [1440, 983], [287, 986]]
vid.generate_mask(points)
vid.make_bg()

vid.save_state(f"{vid.fname}.pckl")

# cv2.imshow("bg", vid.bg_ref[1] / 255.)
# cv2.waitKey(0)
#
# tracker = Tracker(params={"bg_ref": vid.bg_ref[1], "thresh": 99.5})
#
# res = tracker.do_tracking(vid)
# print(res)
# save_outputv(vid, res)
#
# cv2.destroyAllWindows()
