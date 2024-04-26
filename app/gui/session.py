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
            "video": None,
            "tracker": None
        } if "storage" not in kwargs.keys() else kwargs["storage"]

        self.reached = 0 if "reached" not in kwargs.keys() else kwargs["reached"]
        self.current_window_idx = 0 if "current_window_idx" not in kwargs.keys() else kwargs["current_window_idx"]
        self.windows = {
            0: ["Предварительная подготовка видео", VideoPreprocessingWindow],
            1: ["Настройка трекинг", TrackingWindow],
            2: ["Редактор трека", EditTrackWindow],
            3: ["Области интереса", ArenaROIWindow]
        } if "windows" not in kwargs.keys() else kwargs["windows"]

    # def __getstate__(self):
    #     state = {
    #         "storage": self.storage,
    #         "reached": self.reached,
    #         "current_window_idx": self.current_window_idx,
    #         "windows": self.windows
    #     }
    #
    #     return state

    def __getstate__(self):
        state = {
            "storage": self.storage,
            "reached": self.reached,
            "current_window_idx": self.current_window_idx,
            "windows": {
                0: [self.windows[0][0],
                    self.windows[0][1].__getstate__() if self.reached >= 0 else self.windows[0][1]
                    ],
                1: [self.windows[1][0],
                    self.windows[1][1].__getstate__() if self.reached >= 1 else self.windows[1][1]
                    ],
                2: [self.windows[2][0],
                    self.windows[2][1].__getstate__() if self.reached >= 2 else self.windows[2][1]
                    ],
                3: [self.windows[3][0],
                    self.windows[3][1].__getstate__() if self.reached >= 3 else self.windows[3][1]
                    ]
            }
        }

        return state

    def __setstate__(self, state):
        # self.__dict__.update(state)
        # self.storage = {
        #     "video": Video(state.get("storage", None).get("video", None)),
        #     "tracker": Tracker()
        # }
        self.storage = state.get("storage", {"video": None, "tracker": None})
        self.reached = state.get("reached", 0)
        self.current_window_idx = state.get("current_window_idx", 0)
        self.windows = {
            0: ["Предварительная подготовка видео", VideoPreprocessingWindow],
            1: ["Настройка трекинг", TrackingWindow],
            2: ["Редактор трека", EditTrackWindow],
            3: ["Области интереса", ArenaROIWindow]
        }
        for idx, window in state.get("windows", {}).items():
            if idx <= self.reached:
                # print(type(window[1]))
                # print(window[1])
                # self.windows[idx][1] = self.windows[idx][1].__setstate__(window[1])
                self.windows[idx][1] = self.windows[idx][1]()
                self.windows[idx][1].__setstate__(window[1])

    # def __setstate__(self, state): # TODO: Redefine to serialize and deserealize
    #     # self.logger = state["logger"]
    #     self.storage = state["storage"]
    #     self.reached = state["reached"]
    #     self.current_window_idx = state["current_window_idx"]
    #     self.windows = state["windows"]

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
                    print()
                    pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
                except Exception as e:
                    print(e)

    def load_from_file(self, fpath):
        if fpath:
            with open(fpath, 'rb') as f:
                try:
                    state = pickle.loads(f.read())
                    print(state)
                    # self.__dict__.update(state)
                    self.__setstate__(state)
                except Exception as e:
                    print(e)
