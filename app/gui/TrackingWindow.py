import logging

import cv2
from PyQt5.QtCore import QSettings
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlCombo
from pyforms.controls import ControlPlayer
from pyforms.controls import ControlButton
from pyforms.controls import ControlSlider

from app.gui.controls.VideoPlayer import VideoPlayer
from app.src.tracker import Tracker, save_outputv
from app.src.video import Video
from app.gui.PreviewWindow import PreviewWindow


CONFIG_FILE_PATH = '../config.ini'


class TrackingWindow(Video, BaseWidget):

    # def __init__(self, vid: Video, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        # Video.__init__(self, *args, **kwargs)
        Video.__init__(self, fpath="../src/test.avi")
        BaseWidget.__init__(self, 'Настройка трекинга')
        self.logger = logging.getLogger(__name__)

        # self.video = Video()
        # self.video.load_state("current_video.pckl")
        # self.video = vid
        self.tracker = Tracker()
        # self.tracker = tracker

        self._selmethod = ControlCombo('Метод фона')
        for item in ["median", "mean", "max", "min"]:
            self._selmethod.add_item(item)
        self._player = VideoPlayer('Player')
        self._player.value = self.fpath
        self._previewbutton = ControlButton('Preview background')
        self._runbutton = ControlButton('Run tracking')
        self._threshold = ControlSlider(label='Threshold', default=995, minimum=0, maximum=1000)

        self._player.process_frame_event = self.__process_frame

        self._selmethod.changed_event = self.__bgmethodChangeEvent

        self._previewbutton.value = self.__previewEvent

        self._runbutton.value = self.__runEvent

        self._threshold.changed_event = self.__threshChangeEvent

        self._formset = [
            ('_selmethod', '_previewbutton'),
            '_threshold',
            '_player',
            '_runbutton'
        ]

    def __getstate__(self):
        state = self.get_video_state()
        state["tracker"] = self.tracker
        state["_player.value"] = self.fpath
        state["_threshold.value"] = self._threshold.value

        return state

    def __setstate__(self, state):
        self.init_video(**state)

        # self.tracker = state.get("tracker", Tracker())
        videofile = state.get("_player.value", self.fpath)
        if videofile:
            self._player.value = videofile
        self._threshold.value = state.get("_threshold.value", 995)

    # def __getstate__(self):
    #     state = {
    #         "video": self.video,
    #         "tracker": self.tracker
    #     }
    #     return state
    #
    # def save_win_state(self):
    #     settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
    #     settings.setValue('TRWin/WindowState', self.save_form())
    #
    # def load_win_state(self):
    #     settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
    #
    #     state = settings.value('TRWin/WindowState')
    #     if state:
    #         self.load_form(state)

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

    def __process_frame(self, frame):
        frame = self.preprocess_frame(frame)

        return frame

    def __bgmethodChangeEvent(self):
        self.bg_ref[0] = self._selmethod.value
        self.bg_ref[1] = None

    def __previewEvent(self):
        self.make_bg()
        # self.video.save_state("app/gui/current_video.pckl")

        frame = self.bg_ref[1]
        win = PreviewWindow(frame=frame)
        win.parent = self
        win.show()

    def __runEvent(self):
        self.tracker.params["bg_ref"] = self.bg_ref[1]
        self.tracker.params["thresh"] = self._threshold.value / 10
        df = self.tracker.do_tracking(self)
        print(df.head(20))
        save_outputv(self)
        # self.video.save_state("app/gui/current_video.pckl")

    def __threshChangeEvent(self):
        self.tracker.params["thresh"] = self._threshold.value / 10


if __name__ == '__main__':
    from pyforms import start_app

    start_app(TrackingWindow)
