import logging
import pickle

from app.gui.ArenaROIWindow import ArenaROIWindow
from app.gui.EditTrackWindow import EditTrackWindow
from app.gui.TrackingWindow import TrackingWindow
from app.gui.VideoPreprocessingWindow import VideoPreprocessingWindow
from app.src.tracker import Tracker
from app.src.video import Video

CONFIG_FILE_PATH = '../config.ini'


class Session(object):

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)

        self.storage = {
            "video": Video(),
            "tracker": Tracker()
        } if "storage" not in kwargs.keys() else kwargs["storage"]

        self.reached = 0 if "reached" not in kwargs.keys() else kwargs["reached"]
        self.current_window_idx = 0 if "current_window_idx" not in kwargs.keys() else kwargs["current_window_idx"]
        self.windows = {
            0: ["Предварительная подготовка видео", VideoPreprocessingWindow()],
            1: ["Настройка трекинг", TrackingWindow],
            2: ["Редактор трека", EditTrackWindow],
            3: ["Области интереса", ArenaROIWindow]
        } if "windows" not in kwargs.keys() else kwargs["windows"]

    def __setstate__(self, state): # TODO: Redefine to serialize and deserealize
        self.logger = state["logger"]
        self.storage = state["storage"]
        self.reached = state["reached"]
        self.current_window_idx = state["current_window_idx"]

        self.windows = {
            0: ["Предварительная подготовка видео", VideoPreprocessingWindow()],
            1: ["Настройка трекинг", TrackingWindow],
            2: ["Редактор трека", EditTrackWindow],
            3: ["Области интереса", ArenaROIWindow]
        }


    def save_to_file(self, fpath):
        if fpath:
            fpath = fpath.split(".")
            fpath = fpath[0]
            with open(fpath + ".atpr", 'wb') as f:
                # data = self.__dict__
                # data.pop("_mainmenu")
                # print(data.keys())
                # print(data.values())
                try:
                    pickle.dump(self.__dict__, f, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception as e:
                    print(e)

    def load_from_file(self, fpath):
        if fpath:
            with open(fpath, 'rb') as f:
                try:
                    state = pickle.load(f)
                    print(state)
                    self.__dict__ = state
                except Exception as e:
                    print(e)
