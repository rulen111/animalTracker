import pathlib
import pickle

import numpy as np

from PyQt5.QtCore import QSettings
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlCombo
from pyforms.controls import ControlButton
from pyforms.controls import ControlSlider

from app.gui.controls.VideoPlayer import VideoPlayer
from app.cli.preprocessing import Preprocessing
from app.cli.tracking import Tracking
from app.cli.video import Video
from app.gui.PreviewWindow import PreviewWindow


CONFIG_FILE_PATH = '../config.ini'
OBJECT_FILE_PATH = "../session.atr"


class TrackingWindow(Preprocessing, Tracking, BaseWidget):  # TODO: Interactive threshold definition (draw blobs on
    # frame in player)

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Настройка трекинга')
        Preprocessing.__init__(self, *args, **kwargs)
        Tracking.__init__(self, *args, **kwargs)
        # self.logger = logging.getLogger(__name__)

        self.video = Video()
        self.video.load(OBJECT_FILE_PATH)

        self._selmethod = ControlCombo('Метод фона')
        for item in ["median", "mean", "max", "min"]:
            self._selmethod.add_item(item)
        self._selmethod.changed_event = self.__bgmethodChangeEvent

        self._player = VideoPlayer('Player')
        self._player.value = self.video.fpath
        self._player.process_frame_event = self.__process_frame

        self._previewbutton = ControlButton('Preview background')
        self._previewbutton.value = self.__previewEvent

        self._runbutton = ControlButton('Run tracking')
        self._runbutton.value = self.__runEvent

        self._threshold = ControlSlider(label='Threshold', default=995, minimum=0, maximum=1000)
        self._threshold.changed_event = self.__threshChangeEvent

        self._formset = (
            [
                '_selmethod',
                '_previewbutton',
                '_threshold',
                '_runbutton'
            ],
            "||",
            '_player'
        )

        self.load_win_state()

    def save_win_state(self):
        self.video.save(OBJECT_FILE_PATH)
        Preprocessing.save(self, OBJECT_FILE_PATH)
        Tracking.save(self, OBJECT_FILE_PATH)

        # session = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        #
        # session.setValue('TRWin/WindowState', self.save_form())
        # session.setValue('TRWin/Geometry', self.saveGeometry())

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                temp = pickle.load(f)
        else:
            temp = {}

        temp.update({
            "TRWin": {
                "WindowState": self.save_form(),
                "Geometry": self.saveGeometry(),
            },
        })

        with open(OBJECT_FILE_PATH, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_win_state(self):
        self.video.load(OBJECT_FILE_PATH)

        Preprocessing.load(self, OBJECT_FILE_PATH)
        Tracking.load(self, OBJECT_FILE_PATH)

        # session = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        #
        # state = session.value('TRWin/WindowState')
        # if state:
        #     self.load_form(state)
        #
        # geometry = session.value('TRWin/Geometry')
        # if geometry:
        #     self.restoreGeometry(geometry)

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                entries = pickle.load(f)
        else:
            return

        session = entries.get("TRWin", {})

        state = session.get('WindowState', None)
        if state:
            self.load_form(state)

        geometry = session.get('Geometry', None)
        if geometry:
            self.restoreGeometry(geometry)

    def __process_frame(self, frame):  # TODO: User-defined parameters from file?
        frame = self.preprocess_frame(frame)

        return frame

    def __bgmethodChangeEvent(self):
        self.bg_method = self._selmethod.value
        self.bg_img = np.array([])

    def __previewEvent(self):
        self.make_bg(self.video, self)

        frame = self.bg_img
        win = PreviewWindow(frame=frame)
        win.parent = self
        win.show()

    def __runEvent(self):
        df = self.do_tracking(self.video, self)
        self.video.track = df

        self.video.save(OBJECT_FILE_PATH)
        self.video.track.to_csv(f"../track.csv", encoding='utf-8', index=False)

    def __threshChangeEvent(self):
        self.threshold = self._threshold.value / 10

    def closeEvent(self, event):
        self.save_win_state()
        super().closeEvent(event)


if __name__ == '__main__':
    from pyforms import start_app
    from confapp import conf
    import settings

    conf += settings

    start_app(TrackingWindow)
