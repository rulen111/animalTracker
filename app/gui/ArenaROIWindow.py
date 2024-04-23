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


class ArenaROIWindow(BaseWidget):

    # def __init__(self, vid: Video, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Области интереса')
        self.logger = logging.getLogger(__name__)

        self.video = Video()
        self.video.load_state("current_video.pckl")
        # self.video = vid

        self.points_to_draw = []
        self.draw_lines = False

        self.cap = cv2.VideoCapture(self.video.fpath)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.video.tr_range[0])
        ret, frame = self.cap.read()
        frame = self.video.preprocess_frame(frame)
        self._frameimg = ControlImage()
        self._frameimg.value = frame

        self._addbutton = ControlButton("Добавить область")
        self._clearbutton = ControlButton("Очистить кадр")

        self._roiname = ControlText("Имя")

        self._frameslider = ControlSlider(default=1, minimum=1, maximum=len(self.video.track))
        self._roilist = ControlList('Области интереса')

        self._frameslider.changed_event = self.__frameSelectionEvent
        self.keyPressEvent = self.__drawPolyEvent

        self._frameimg.click_event = self.__addPointEvent
        self._frameimg.double_click_event = self.__drawPolyEvent

        self._addbutton.value = self.__addRoiEvent
        self._clearbutton.value = self.__clearCanvasEvent

        self.closeEvent = self.__formClosedEvent

        self.formset = [
            ('_frameimg', '_roilist'),
            ('_frameslider', '_roiname', '_addbutton', '_clearbutton')
        ]

    def __getstate__(self):
        state = {
            "video": self.video
        }
        return state

    def save_win_state(self):
        settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        settings.setValue('ROIWin_WindowState', self.save_form())

    def load_win_state(self):
        settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)

        state = settings.value('ROIWin_WindowState')
        if state:
            self.load_form(state)

    def __formClosedEvent(self, event):
        self.cap.release()
        return event

    def __frameSelectionEvent(self):
        current_frame = int(self._frameslider.value)

        self.cap.set(cv2.CAP_PROP_POS_FRAMES,
                     self.video.tr_range[0] + (current_frame - 1)
                     )
        ret, frame = self.cap.read()
        frame = self.video.preprocess_frame(frame)

        if self.video.roi:
            for key, item in self.video.roi.items():
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
            self.video.roi[self._roiname.value] = self.points_to_draw
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
