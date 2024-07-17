import logging
import pathlib
import pickle

import pandas as pd
from confapp import conf

import cv2
import numpy as np
from PyQt5.QtCore import QSettings
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlImage
from pyforms.controls import ControlSlider
from pyforms.controls import ControlList
from pyforms.controls import ControlButton
from pyforms.controls import ControlText

from app.cli.preprocessing import Preprocessing
from app.cli.roi import ROI
from app.cli.video import Video


CONFIG_FILE_PATH = '../config.ini'
OBJECT_FILE_PATH = "../session.atr"


class ArenaROIWindow(Preprocessing, ROI, BaseWidget):
    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Области интереса')
        Preprocessing.__init__(self, resolution=0.5, tracking_interval=(300, 1000))
        ROI.__init__(self, *args, **kwargs)
        # self.logger = logging.getLogger(__name__)

        self.points_to_draw = []
        self.draw_lines = False

        self.video = Video()
        self.video.load(OBJECT_FILE_PATH)

        self._frameimg = ControlImage()
        if self.video.fpath:
            cap = cv2.VideoCapture(self.video.fpath)
            cap.set(cv2.CAP_PROP_POS_FRAMES, self.tracking_interval[0])
            ret, frame = cap.read()
            frame = self.preprocess_frame(frame)
            self._frameimg.value = frame
            cap.release()
        self._frameimg.click_event = self.__addPointEvent
        self._frameimg.double_click_event = self.__drawPolyEvent

        self._addbutton = ControlButton("Добавить область")
        self._addbutton.value = self.__addRoiEvent

        self._clearbutton = ControlButton("Очистить кадр")
        self._clearbutton.value = self.__clearCanvasEvent

        self._roiname = ControlText("Имя")

        self._frameslider = ControlSlider(default=1, minimum=1,
                                          maximum=len(self.video.track) if np.any(self.video.track) else 2)
        self._frameslider.changed_event = self.__frameSelectionEvent

        self._roilist = ControlList('Области интереса')

        self.keyPressEvent = self.__drawPolyEvent

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

        self.load_win_state()

    def save_win_state(self):
        self.video.save(OBJECT_FILE_PATH)
        Preprocessing.save(self, OBJECT_FILE_PATH)
        ROI.save(self, OBJECT_FILE_PATH)

        # session = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        #
        # session.setValue('ROIWin/WindowState', self.save_form())
        # session.setValue('ROIWin/Geometry', self.saveGeometry())
        #
        # session.setValue("ROIWin/points_to_draw", self.points_to_draw if self.points_to_draw else "empty")
        # session.setValue("ROIWin/draw_lines", 1 if self.draw_lines else 0)

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                temp = pickle.load(f)
        else:
            temp = {}

        temp.update({
            "ROIWin": {
                "WindowState": self.save_form(),
                "Geometry": self.saveGeometry(),
                "points_to_draw": self.points_to_draw if self.points_to_draw else "empty",
                "draw_lines": 1 if self.draw_lines else 0,
            },
        })

        with open(OBJECT_FILE_PATH, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_win_state(self):
        self.video.load(OBJECT_FILE_PATH)
        Preprocessing.load(self, OBJECT_FILE_PATH)
        ROI.load(self, OBJECT_FILE_PATH)

        # session = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        #
        # state = session.value('ROIWin/WindowState')
        # if state:
        #     self.load_form(state)
        #
        # geometry = session.value('ROIWin/Geometry')
        # if geometry:
        #     self.restoreGeometry(geometry)
        #
        # self.points_to_draw = session.value("ROIWin/points_to_draw", [])
        # self.points_to_draw = [] if self.points_to_draw == "empty" else self.points_to_draw
        # self.draw_lines = bool(int(session.value("ROIWin/draw_lines", 0)))

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                entries = pickle.load(f)
        else:
            return

        session = entries.get("ROIWin", {})

        state = session.get('WindowState', None)
        if state:
            self.load_form(state)

        geometry = session.get('Geometry', None)
        if geometry:
            self.restoreGeometry(geometry)

        self.points_to_draw = session.get("points_to_draw", [])
        self.points_to_draw = [] if self.points_to_draw == "empty" else self.points_to_draw
        self.draw_lines = bool(int(session.get("draw_lines", 0)))

    def __frameSelectionEvent(self):
        current_frame = int(self._frameslider.value)

        cap = cv2.VideoCapture(self.video.fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES,
                self.tracking_interval[0] + (current_frame - 1)
                )
        ret, frame = cap.read()
        frame = self.preprocess_frame(frame)

        if self.roi_dict:
            for key, item in self.roi_dict.items():
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
            self.roi_dict[self._roiname.value] = self.points_to_draw
            roistring = f"{self._roiname.value}: {self.points_to_draw}"
            self._roilist.__add__([roistring])
            self.points_to_draw = []
            self.draw_lines = False
            self._roiname.value = ""
            self.video.save(OBJECT_FILE_PATH)
            # self.video.save_state("current_video.pckl")
            self.__frameSelectionEvent()

    def __clearCanvasEvent(self):
        self.points_to_draw = []
        self.draw_lines = False
        self.__frameSelectionEvent()

    def closeEvent(self, event):
        self.save_win_state()
        super().closeEvent(event)


if __name__ == '__main__':
    from pyforms import start_app
    from confapp import conf
    import settings

    conf += settings

    start_app(ArenaROIWindow)
