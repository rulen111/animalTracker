import logging
import pickle
from confapp import conf

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlList
from pyforms.controls import ControlButton

from app.gui.ArenaROIWindow import ArenaROIWindow
from app.gui.EditTrackWindow import EditTrackWindow
from app.gui.TrackingWindow import TrackingWindow
from app.gui.VideoPreprocessingWindow import VideoPreprocessingWindow
from app.gui.session import Session
# from app.cli.tracker import Tracker
from app.cli.video import Video

CONFIG_FILE_PATH = '../config.ini'


class MainWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Animal Tracker')
        # Session().__init__(**kwargs) # НЕ уверен

        # self.gui = [VideoPreprocessingWindow, TrackingWindow, EditTrackWindow, ArenaROIWindow]
        # self.gui = {
        #     "Предварительная подготовка видео": VideoPreprocessingWindow,
        #     "Настройка трекинг": TrackingWindow,
        #     "Редактор трека": EditTrackWindow,
        #     "Области интереса": ArenaROIWindow
        # }
        self.logger = logging.getLogger(__name__)

        # self.windows = {
        #     0: ("Предварительная подготовка видео", VideoPreprocessingWindow),
        #     1: ("Настройка трекинг", TrackingWindow),
        #     2: ("Редактор трека", EditTrackWindow),
        #     3: ("Области интереса", ArenaROIWindow)
        # }

        # self.session = Session() if "session" not in kwargs.keys() else kwargs["session"]
        self.session = kwargs.get("session", Session())

        # self.storage = {
        #     "video": Video(),
        #     "tracker": Tracker()
        # } if "storage" not in kwargs.keys() else kwargs["storage"]
        # self.reached = 0 if "reached" not in kwargs.keys() else kwargs["reached"]

        # self.current_window_idx = 0 if "current_window_idx" not in kwargs.keys() else kwargs["current_window_idx"]
        # self.windows = {
        #     0: ["Предварительная подготовка видео", VideoPreprocessingWindow()],
        #     1: ["Настройка трекинг", TrackingWindow],
        #     2: ["Редактор трека", EditTrackWindow],
        #     3: ["Области интереса", ArenaROIWindow]
        # } if "windows" not in kwargs.keys() else kwargs["windows"]

        self._current_window = self.session.windows[self.session.current_window_idx][1]()
        self._current_window.parent = self

        self._panel = ControlEmptyWidget()
        self._panel.value = self._current_window

        self._winlist = ControlList("Разделы")
        for idx, window in self.session.windows.items():
            self._winlist.__add__([window[0]])
        self._winlist.readonly = True

        self._nextbutton = ControlButton("Далее")
        self._nextbutton.value = self.__nextWindowEvent

        self._backbutton = ControlButton("Назад")
        self._backbutton.value = self.__prevWindowEvent

        # self.formset = [
        #     ('_winlist', '_panel'),
        #     ('_backbutton', '_nextbutton')
        # ]

        self.formset = (
            '_winlist',
            "||",
            [
                '_panel',
                "=",
                (
                    '_backbutton',
                    '_nextbutton'
                )
            ]
        )

        self.mainmenu = [
            {'File': [
                {"Open": self.__open},
                {'Save as': self.__save_as}
            ]
            }
        ]

    # def __getstate__(self):
    #     state = {
    #         'storage': self.storage,
    #         'reached': self.reached,
    #         'current_window_idx': self.current_window_idx,
    #         'windows': self.windows,
    #         'current_window': self.current_window
    #     }
    #     return state

    # def __setstate__(self, state):
    #     self.__init__(
    #         storage=state['storage'], reached=state['reached'],
    #         current_window_idx=state['current_window_idx'], windows=state['windows'],
    #         current_window=state['current_window']
    #         )
    #     print("tut")
    #     print(self.current_window)
    #     # self._panel.value = self.current_window

    def __save_as(self):  # TODO
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filter = "Animal Tracker Project(*.atpr)"
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            "Save File", "",
                                                            filter=filter,
                                                            options=options)

        # self.session.save_to_file(fileName)
        if fileName:
            fpath = fileName.split(".")
            fpath = fpath[0]
            with open(fpath + ".atpr", 'wb') as f:
                # data = self.__dict__
                # data.pop("_mainmenu")
                # print(data.keys())
                # print(data.values())
                try:
                    # print(self.session.__getstate__())
                    pickle.dump(self.session.__getstate__(), f, pickle.HIGHEST_PROTOCOL)
                except Exception as e:
                    print(e)

    def __open(self):  # TODO
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filter = "Animal Tracker Project(*.atpr)"
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            "Open File", "",
                                                            filter=filter,
                                                            options=options)

        # self.session.load_from_file(fileName)
        # self.current_window = self.session.windows[self.session.current_window_idx][1]
        # self.current_window.parent = self
        # self._panel.value = self.current_window
        if fileName:
            with open(fileName, 'rb') as f:
                try:
                    # self.session = pickle.load(f)
                    state = pickle.load(f)
                    # print(state)
                    self.session.__setstate__(state)
                    # self.__dict__.update(state)
                    # self.__setstate__(state)
                    self._current_window = self.session.windows[self.session.current_window_idx][1]
                    self._current_window.parent = self
                    self._panel.value = self._current_window
                except Exception as e:
                    print(e)

    def __update_windows(self):
        # for k, item in self.windows.items():
        #     self.windows[k] = item[1](self.storage["video"]) if self.reached >= k else item[1]
        self.session.windows = {
            0: ["Предварительная подготовка видео",
                self.session.windows[0][1]
                ],
            1: ["Настройка трекинг",
                TrackingWindow(**self.session.storage["video"]) if self.session.reached == 1 else self.session.windows[1][1]
                ],
            2: ["Редактор трека",
                EditTrackWindow(**self.session.storage["video"]) if self.session.reached == 2 else self.session.windows[2][1]
                ],
            3: ["Области интереса",
                ArenaROIWindow(**self.session.storage["video"]) if self.session.reached == 3 else self.session.windows[3][1]
                ]
        }

    def __nextWindowEvent(self):
        self.session.current_window_idx += 1
        if ((self.session.reached < (len(self.session.windows.keys()) - 1))
                and (self.session.reached < self.session.current_window_idx)):
            self.session.reached += 1
            self.session.storage["video"] = self._current_window.get_video_state()
            self.__update_windows()

        if self.session.current_window_idx < len(self.session.windows.keys()):
            self.session.windows[self.session.current_window_idx - 1][1] = self._current_window
            self.session.storage["video"] = self._current_window.get_video_state()
            self._current_window = self.session.windows[self.session.current_window_idx][1]
            # self.current_window.video = self.session.storage["video"]
            self._current_window.init_video(**self.session.storage["video"])
            self._panel.value = self._current_window
        else:
            return

        # self.current_window.save_win_state()
        # if (self.reached < len(self.windows.keys())) and (self.reached < self.current_window_idx):
        #     self.reached += 1
        #     self.__update_windows()
        #
        # if self.current_window_idx < len(self.windows.keys()):
        #     self.current_window_idx += 1
        #     self.current_window = self.windows[self.current_window_idx][1]
        #     # self.current_window.load_win_state()
        #
        #     self._panel.value = self.current_window
        # else:
        #     return

    def __prevWindowEvent(self):
        # self.current_window.save_win_state()
        if self.session.current_window_idx > 0:
            self.session.windows[self.session.current_window_idx][1] = self._current_window
            self.session.storage["video"] = self._current_window.get_video_state()
            self.session.current_window_idx -= 1
            self._current_window = self.session.windows[self.session.current_window_idx][1]
            # self.current_window.video = self.session.storage["video"]
            self._current_window.init_video(**self.session.storage["video"])
            # self.current_window.load_win_state()
            self._panel.value = self._current_window
        else:
            return


if __name__ == '__main__':
    from pyforms import start_app
    from confapp import conf
    import settings

    conf += settings

    start_app(MainWindow)
