import logging

import cv2
import numpy as np
from PyQt5.QtCore import QSettings
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlImage
from pyforms.controls import ControlSlider
from pyforms.controls import ControlList
from pyforms.controls import ControlButton
from pyforms.controls import ControlText

from app.src.video import Video


CONFIG_FILE_PATH = '../config.ini'


class ArenaROIWindow(Video, BaseWidget):

    # def __init__(self, vid: Video, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        Video.__init__(self, *args, **kwargs)
        # Video.__init__(self, fpath="../src/test.avi")
        BaseWidget.__init__(self, 'Области интереса')
        self.logger = logging.getLogger(__name__)

        # self.video = Video()
        # self.video.load_state("current_video.pckl")
        # self.video = vid

        self.points_to_draw = []
        self.draw_lines = False

        cap = cv2.VideoCapture(self.fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.tr_range[0])
        ret, frame = cap.read()
        frame = self.preprocess_frame(frame)
        self._frameimg = ControlImage()
        self._frameimg.value = frame
        cap.release()

        self._addbutton = ControlButton("Добавить область")
        self._clearbutton = ControlButton("Очистить кадр")

        self._roiname = ControlText("Имя")

        self._frameslider = ControlSlider(default=1, minimum=1, maximum=len(self.track) if np.any(self.track) else 2)
        self._roilist = ControlList('Области интереса')

        self._frameslider.changed_event = self.__frameSelectionEvent
        self.keyPressEvent = self.__drawPolyEvent

        self._frameimg.click_event = self.__addPointEvent
        self._frameimg.double_click_event = self.__drawPolyEvent

        self._addbutton.value = self.__addRoiEvent
        self._clearbutton.value = self.__clearCanvasEvent

        # self.closeEvent = self.__formClosedEvent

        # self.formset = [
        #     ('_frameimg', '_roilist'),
        #     ('_frameslider', '_roiname', '_addbutton', '_clearbutton')
        # ]
        self.formset = (
            [
                '_frameimg',
                '_frameslider'
            ],
            "||",
            [
                '_roilist',
                (
                    '_roiname',
                    '_addbutton',
                    '_clearbutton'
                )
            ]
        )

    def __getstate__(self):
        state = self.get_video_state()
        state["points_to_draw"] = self.points_to_draw
        state["draw_lines"] = self.draw_lines
        state["_frameimg.value"] = self._frameimg.value
        state["_frameslider.value"] = self._frameslider.value
        state["_roilist.value"] = self._roilist.value

        return state

    def __setstate__(self, state):
        self.init_video(**state)

        self.points_to_draw = state.get("points_to_draw", [])
        self.draw_lines = state.get("draw_lines", False)
        img = state.get("_frameimg.value", None)
        if img:
            self._frameimg.value = img
        self._frameslider.value = state.get("_frameslider.value", 1)
        rois = state.get("_roilist.value", None)
        if rois:
            self._roilist.value = rois

    # def __getstate__(self):
    #     state = {
    #         "video": self.video
    #     }
    #     return state
    #
    # def save_win_state(self):
    #     settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
    #     settings.setValue('ROIWin_WindowState', self.save_form())
    #
    # def load_win_state(self):
    #     settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
    #
    #     state = settings.value('ROIWin_WindowState')
    #     if state:
    #         self.load_form(state)
    #
    # def __formClosedEvent(self, event):
    #     self.cap.release()
    #     return event

    def init_video(self, *args, **kwargs):
        for key, value in kwargs.items():
            if key in self.__dict__.keys():
                self.__dict__[key] = value

    def get_video_state(self):
        state = {
            "fpath": self.fpath,
            "folder": self.folder,
            "fname": self.fname,
            "bg_fpath": self.bg_fpath,
            "dsmpl": self.dsmpl,
            "bg_ref": self.bg_ref,
            "frame_cnt": self.frame_cnt,
            "frame_rate": self.frame_rate,
            "shape": self.shape,
            "tr_range": self.tr_range,
            "tracked": self.tracked,
            "track": self.track,
            "mask": self.mask,
            "roi": self.roi
        }

        return state

    def __frameSelectionEvent(self):
        current_frame = int(self._frameslider.value)

        cap = cv2.VideoCapture(self.fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES,
                self.tr_range[0] + (current_frame - 1)
                )
        ret, frame = cap.read()
        frame = self.preprocess_frame(frame)

        if self.roi:
            for key, item in self.roi.items():
                points = np.array(item)
                frame = cv2.polylines(frame, [points], True, (0, 0, 255))
                frame = cv2.putText(frame, key,
                                    (points[0][0], points[0][1]), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (0, 0, 255), 1, cv2.LINE_AA
                                    )

        if self.points_to_draw:
            for point in self.points_to_draw:
                x = point[0]
                y = point[1]
                frame = cv2.circle(frame, (x, y), radius=5, color=(0, 0, 255), thickness=-1)

        if self.draw_lines:
            points = np.array(self.points_to_draw)
            frame = cv2.polylines(frame, [points], True, (0, 0, 255))

        self._frameimg.value = frame

    def __addPointEvent(self, event, x, y):
        frame = self._frameimg.value
        self.points_to_draw += [[int(x), int(y)]]
        frame = cv2.circle(frame, (int(x), int(y)), radius=5, color=(0, 0, 255), thickness=-1)
        self._frameimg.value = frame
        return event, x, y

    def __drawPolyEvent(self, event):
        if event.key() == 16777220 and len(self.points_to_draw) >= 3:
            frame = self._frameimg.value
            self.draw_lines = True
            points = np.array(self.points_to_draw)
            frame = cv2.polylines(frame, [points], True, (0, 0, 255))
            # self.points_to_draw = []
            self._frameimg.value = frame

    def __addRoiEvent(self):
        if self._roiname.value and self.draw_lines:
            self.roi[self._roiname.value] = self.points_to_draw
            roistring = f"{self._roiname.value}: {self.points_to_draw}"
            self._roilist.__add__([roistring])
            self.points_to_draw = []
            self.draw_lines = False
            self._roiname.value = ""
            # self.video.save_state("current_video.pckl")
            self.__frameSelectionEvent()

    def __clearCanvasEvent(self):
        self.points_to_draw = []
        self.draw_lines = False
        self.__frameSelectionEvent()


if __name__ == '__main__':
    from pyforms import start_app

    start_app(ArenaROIWindow)
