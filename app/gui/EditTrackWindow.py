import logging
import pathlib
import pickle

import cv2
import csv
from confapp import conf

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

from app.cli.preprocessing import Preprocessing
from app.cli.video import Video
from app.gui.models.TableModel import TableModel

CONFIG_FILE_PATH = '../config.ini'
OBJECT_FILE_PATH = "../udp.dat"


def draw_track(frame, points):
    cols = points.columns
    for idx, row in points.iterrows():
        # frame = cv2.circle(frame, (point[0], point[1]), radius=1, color=255, thickness=-1)
        x = int(float(row[cols[0]]))
        y = int(float(row[cols[1]]))
        frame = cv2.circle(frame, (x, y), radius=1, color=255, thickness=-1)

    return frame


class EditTrackWindow(Preprocessing, BaseWidget):
    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Редактор трека')
        # Preprocessing.__init__(self, *args, **kwargs)
        Preprocessing.__init__(self, resolution=0.5, tracking_interval=(300, 1000))
        # self.logger = logging.getLogger(__name__)

        self.video = Video()
        self.video.load(OBJECT_FILE_PATH)

        data = self.video.track if np.any(self.video.track) else pd.DataFrame({"X": [0.],
                                                                               "Y": [0.],
                                                                               "Distance_px": [0.]})
        self._model = TableModel(data)

        self._coordtable = ControlTableView("Координаты")
        self._coordtable.setModel(self._model)
        self._coordtable.setSelectionBehavior(QAbstractItemView.SelectRows)

        self._selection_model = self._coordtable.selectionModel()
        self._selection_model.selectionChanged.connect(self.__tableRowSelectionEvent)

        self._frameimg = ControlImage()
        try:
            cap = cv2.VideoCapture(self.video.fpath)
            cap.set(cv2.CAP_PROP_POS_FRAMES, self.tracking_interval[0])
            ret, frame = cap.read()
            frame = self.preprocess_frame(frame)
            self._frameimg.value = frame
            cap.release()
        except Exception:
            pass
        self._frameimg.double_click_event = self.__changePointEvent

        self._frameslider = ControlSlider(default=1, minimum=1,
                                          maximum=len(self.video.track) if np.any(self.video.track) else 2)
        self._frameslider.changed_event = self.__frameSelectionEvent

        self._savebutton = ControlButton('Save track')
        self._savebutton.value = self.__saveTrackButton

        self._formset = (
            [
                '_frameimg',
                '_frameslider'
            ],
            "||",
            [
                '_coordtable',
                '_savebutton'
            ]
        )

        self.load_win_state()

    def save_win_state(self):
        self.video.save(OBJECT_FILE_PATH)
        Preprocessing.save(self, OBJECT_FILE_PATH)

        # session = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        #
        # session.setValue('EditTRWin/WindowState', self.save_form())
        # session.setValue('EditTRWinTRWin/Geometry', self.saveGeometry())

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                temp = pickle.load(f)
        else:
            temp = {}

        temp.update({
            "EditTRWin": {
                "WindowState": self.save_form(),
                "Geometry": self.saveGeometry(),
            },
        })

        with open(OBJECT_FILE_PATH, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_win_state(self):
        self.video.load(OBJECT_FILE_PATH)
        Preprocessing.load(self, OBJECT_FILE_PATH)

        # session = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        #
        # state = session.value('EditTRWin/WindowState')
        # if state:
        #     self.load_form(state)
        #
        # geometry = session.value('EditTRWin/Geometry')
        # if geometry:
        #     self.restoreGeometry(geometry)

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                entries = pickle.load(f)
        else:
            return

        session = entries.get("EditTRWin", {})

        state = session.get('WindowState', None)
        if state:
            self.load_form(state)

        geometry = session.get('Geometry', None)
        if geometry:
            self.restoreGeometry(geometry)

    def init_video(self, *args, **kwargs):  # TODO
        for key, value in kwargs.items():
            if key in self.__dict__.keys():
                self.__dict__[key] = value

    def get_video_state(self):  # TODO
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

        cap = cv2.VideoCapture(self.video.fpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES,
                self.tracking_interval[0] + (current_frame - 1)
                )
        ret, frame = cap.read()
        frame = self.preprocess_frame(frame)

        points = self._model.get_data().iloc[0:current_frame]
        frame = draw_track(frame, points)
        self._frameimg.value = frame

    def __tableRowSelectionEvent(self, selected, deselected):
        if selected.indexes():
            self._frameslider.value = selected.indexes()[-1].row() + 1

    def __changePointEvent(self, event, x, y):
        selected = self._coordtable.selectedIndexes()
        for idx in range(len(selected) // 3):
            self._coordtable.model().setData(index=selected[3 * idx], value=x, role=Qt.EditRole)
            self._coordtable.model().setData(index=selected[3 * idx + 1], value=y, role=Qt.EditRole, dist=True)

        self.__frameSelectionEvent()

        return event, x, y

    def __saveTrackButton(self):
        df_old = self.video.track
        df_edited = self._model.get_data()
        self.video.track = df_edited
        self.video.save(OBJECT_FILE_PATH)

        df_old.to_csv('../track-prev.csv', encoding='utf-8', index=False)
        df_edited.to_csv('../track.csv', encoding='utf-8', index=False)

    def closeEvent(self, event):
        self.save_win_state()
        super().closeEvent(event)


if __name__ == '__main__':
    from pyforms import start_app
    from confapp import conf
    import settings

    conf += settings

    start_app(EditTrackWindow)
