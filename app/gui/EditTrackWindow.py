import logging

import cv2
import csv

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import Qt, QSettings
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlPlayer
from pyforms.controls import ControlTableView
from pyforms.controls import ControlImage
from pyforms.controls import ControlSlider
from pyforms.controls import ControlButton
from pyforms.controls import ControlTree  # TODO:

from app.src.video import Video
from app.gui.models.TableModel import TableModel

CONFIG_FILE_PATH = '../config.ini'


def draw_track(frame, points):
    cols = points.columns
    for idx, row in points.iterrows():
        # frame = cv2.circle(frame, (point[0], point[1]), radius=1, color=255, thickness=-1)
        x = int(float(row[cols[0]]))
        y = int(float(row[cols[1]]))
        frame = cv2.circle(frame, (x, y), radius=1, color=255, thickness=-1)

    return frame


class EditTrackWindow(Video, BaseWidget):

    # def __init__(self, vid: Video, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        Video.__init__(self, *args, **kwargs)
        # Video.__init__(self, fpath="../src/test.avi")
        BaseWidget.__init__(self, 'Редактор трека')
        self.logger = logging.getLogger(__name__)

        # self.video = Video()
        # self.video.load_state("current_video.pckl")
        # self.video = vid

        # data = [[f"{coords[0]:.6}", f"{coords[1]:.6}"]
        #         for coords in zip(self.video.track[0], self.video.track[1])]
        data = self.track if np.any(self.track) else pd.DataFrame({"X": [0.], "Y": [0.], "Distance_px": [0.]})
        self._model = TableModel(data)
        self.multselect = False

        cap = cv2.VideoCapture(self.fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.tr_range[0])
        ret, frame = cap.read()
        frame = self.preprocess_frame(frame)
        self._frameimg = ControlImage()
        self._frameimg.value = frame
        cap.release()

        # self._frameslider = ControlSlider(default=1, minimum=1, maximum=len(self.video.track[0]))
        self._frameslider = ControlSlider(default=1, minimum=1, maximum=len(self.track) if np.any(self.track) else 2)

        # self._player = ControlPlayer('Player')
        # self._player.value = self.video.fpath
        # self._player.value.set(cv2.CAP_PROP_POS_FRAMES, self.video.tr_range[0])

        self._savebutton = ControlButton('Save track')

        self._coordtable = ControlTableView("Координаты")
        self._coordtable.setModel(self._model)
        self.selection_model = self._coordtable.selectionModel()
        self._coordtable.setSelectionBehavior(QAbstractItemView.SelectRows)

        # self.closeEvent = self.__formClosedEvent
        self._frameslider.changed_event = self.__frameSelectionEvent

        self.selection_model.selectionChanged.connect(self.__tableRowSelectionEvent)

        self._frameimg.double_click_event = self.__changePointEvent

        self._savebutton.value = self.__saveTrackButton

        self._formset = [
            ('_frameimg', '_coordtable'),
            ('_frameslider', '_savebutton')
        ]

    def __getstate__(self):
        state = self.get_video_state()
        state["data"] = self._model.get_data()
        state["multselect"] = self.multselect
        state["_frameimg.value"] = self._frameimg.value
        state["_frameslider.value"] = self._frameslider.value

        return state

    def __setstate__(self, state):
        self.init_video(**state)

        data = state.get("data", None)
        if data:
            self._model = TableModel(data)
            self._coordtable.setModel(self._model)
        self.multselect = state.get("multselect", False)
        img = state.get("_frameimg.value", None)
        if img:
            self._frameimg.value = img
        self._frameslider.value = state.get("_frameslider.value", 1)

    # def __getstate__(self):
    #     state = {
    #         "video": self.video,
    #         "multselect": self.multselect
    #     }
    #     return state
    #
    # def save_win_state(self):
    #     settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
    #     settings.setValue('EDTRWin_WindowState', self.save_form())
    #
    # def load_win_state(self):
    #     settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
    #
    #     state = settings.value('EDTRWin_WindowState')
    #     if state:
    #         self.load_form(state)

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

        selected = [idx.row() for idx in self._coordtable.selectedIndexes()]
        if (current_frame - 1) not in selected:
            self._coordtable.selectRow(current_frame - 1)

        cap = cv2.VideoCapture(self.fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES,
                self.tr_range[0] + (current_frame - 1)
                )
        ret, frame = cap.read()
        frame = self.preprocess_frame(frame)
        # points = [[int(coords[0]), int(coords[1])]
        #           for coords in zip(self.video.track[0][:current_frame], self.video.track[1][:current_frame])
        #           ]
        # points = self._model.get_data()[:current_frame]
        points = self._model.get_data().iloc[0:current_frame]
        frame = draw_track(frame, points)
        self._frameimg.value = frame

    def __tableRowSelectionEvent(self, selected, deselected):
        if selected.indexes():
            self._frameslider.value = selected.indexes()[-1].row() + 1

    def __changePointEvent(self, event, x, y):
        # selected = [idx.row() for idx in self._coordtable.selectedIndexes()]
        selected = self._coordtable.selectedIndexes()
        for idx in range(len(selected) // 3):
            # self._coordtable.model().setData(selected[2 * idx], f"{x:.6}", Qt.EditRole)
            # self._coordtable.model().setData(selected[2 * idx + 1], f"{y:.6}", Qt.EditRole)
            self._coordtable.model().setData(index=selected[3 * idx], value=x, role=Qt.EditRole)
            self._coordtable.model().setData(index=selected[3 * idx + 1], value=y, role=Qt.EditRole, dist=True)

        self.__frameSelectionEvent()

        return event, x, y

    def __saveTrackButton(self):
        df_old = self.track
        df_edited = self._model.get_data()
        self.track = df_edited
        df_old.to_csv('coords_orig.csv', encoding='utf-8', index=False)
        df_edited.to_csv('coords_edited.csv', encoding='utf-8', index=False)
        # self.video.save_state("current_video.pckl")


if __name__ == '__main__':
    from pyforms import start_app

    start_app(EditTrackWindow)
