from app.src.tracker import Tracker, save_outputv
from app.src.video import Video
import cv2

vid = Video("test.avi")
vid.dsmpl = 0.5
vid.tr_range = (300, 1000)
vid.bg_ref[0] = "median"
vid.make_bg()

while True:
    cv2.imshow('ref', vid.bg_ref[1] / 255.)
    if cv2.waitKey(30) == ord('q'):
        break

tracker = Tracker(params={"bg_ref": vid.bg_ref[1], "thresh": 99.5})

res = tracker.do_tracking(vid)
print(res)
save_outputv(vid, res)

cv2.destroyAllWindows()
