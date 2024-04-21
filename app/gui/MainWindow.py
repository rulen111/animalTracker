import logging
import pickle

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
from app.src.tracker import Tracker
from app.src.video import Video

CONFIG_FILE_PATH = '../config.ini'


class MainWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Animal Tracker')

        # self.gui = [VideoPreprocessingWindow, TrackingWindow, EditTrackWindow, ArenaROIWindow]
        # self.gui = {
        #     "Предварительная подготовка видео": VideoPreprocessingWindow,
        #     "Настройка трекинг": TrackingWindow,
        #     "Редактор трека": EditTrackWindow,
        #     "Области интереса": ArenaROIWindow
        # }
        self._logger = logging.getLogger(__name__)

        # self.windows = {
        #     0: ("Предварительная подготовка видео", VideoPreprocessingWindow),
        #     1: ("Настройка трекинг", TrackingWindow),
        #     2: ("Редактор трека", EditTrackWindow),
        #     3: ("Области интереса", ArenaROIWindow)
        # }

        self.storage = {
            "video": Video(),
            "tracker": Tracker()
        }
        self.reached = 0
        # self.windows = {
        #     0: ("Предварительная подготовка видео",
        #         VideoPreprocessingWindow(self.storage["video"])
        #         ),
        #     1: ("Настройка трекинг", TrackingWindow(self.storage["video"], self.storage["tracker"])),
        #     2: ("Редактор трека", EditTrackWindow(self.storage["video"])),
        #     3: ("Области интереса", ArenaROIWindow(self.storage["video"]))
        # }
        self.current_window_idx = 0
        self.windows = {
            0: ["Предварительная подготовка видео", VideoPreprocessingWindow()],
            1: ["Настройка трекинг", TrackingWindow],
            2: ["Редактор трека", EditTrackWindow],
            3: ["Области интереса", ArenaROIWindow]
        }

        self._panel = ControlEmptyWidget()
        self.current_window = self.windows[self.current_window_idx][1]
        self.current_window.parent = self
        self._panel.value = self.current_window

        self._winlist = ControlList("Разделы")
        for idx, window in self.windows.items():
            self._winlist.__add__([window[0]])
        self._winlist.readonly = True

        self._nextbutton = ControlButton("Далее")
        self._backbutton = ControlButton("Назад")

        self._nextbutton.value = self.__nextWindowEvent
        self._backbutton.value = self.__prevWindowEvent

        self.formset = [
            ('_winlist', '_panel'),
            ('_backbutton', '_nextbutton')
        ]

        self.mainmenu = [
            {'File': [
                {"Open": self.__open},
                {'Save as': self.__save_as}
            ]
            }
        ]

    def __getstate__(self):
        state = {
            'storage': self.storage,
            'reached': self.reached,
            'current_window_idx': self.current_window_idx,
            'windows': self.windows,
            'current_window': self.current_window
        }
        return state

    def __setstate__(self, state):
        for attr, value in state.items():
            self.__dict__[attr] = value

    def __save_as(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filter = "Animal Tracker Project(*.atrprj)"
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            "Save File", "",
                                                            filter=filter,
                                                            options=options)
        if fileName:
            with open(fileName.strip(".atrprj") + ".atrprj", 'wb') as f:
                # data = self.__dict__
                # data.pop("_mainmenu")
                # print(data.keys())
                # print(data.values())
                try:
                    pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception as e:
                    print(e.args)

    def __open(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filter = "Animal Tracker Project(*.atrprj)"
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            "Open File", "",
                                                            filter=filter,
                                                            options=options)
        if fileName:
            print(fileName)
            with open(fileName, 'rb') as f:
                try:
                    state = pickle.load(f)
                    self.__setstate__(state)
                except Exception as e:
                    print(e.args)


    def __update_windows(self):
        # for k, item in self.windows.items():
        #     self.windows[k] = item[1](self.storage["video"]) if self.reached >= k else item[1]
        self.windows = {
            0: ["Предварительная подготовка видео",
                self.windows[0][1]
                ],
            1: ["Настройка трекинг",
                TrackingWindow(self.storage["video"]) if self.reached == 1 else self.windows[1][1]
                ],
            2: ["Редактор трека",
                EditTrackWindow(self.storage["video"]) if self.reached == 2 else self.windows[2][1]
                ],
            3: ["Области интереса",
                ArenaROIWindow(self.storage["video"]) if self.reached == 3 else self.windows[3][1]
                ]
        }

    def __nextWindowEvent(self):
        self.current_window_idx += 1
        if (self.reached < (len(self.windows.keys()) - 1)) and (self.reached < self.current_window_idx):
            self.reached += 1
            self.storage["video"] = self.current_window.video
            self.__update_windows()

        if self.current_window_idx < len(self.windows.keys()):
            self.windows[self.current_window_idx - 1][1] = self.current_window
            self.storage["video"] = self.current_window.video
            self.current_window = self.windows[self.current_window_idx][1]
            self.current_window.video = self.storage["video"]
            self._panel.value = self.current_window
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
        if self.current_window_idx > 0:
            self.windows[self.current_window_idx][1] = self.current_window
            self.storage["video"] = self.current_window.video
            self.current_window_idx -= 1
            self.current_window = self.windows[self.current_window_idx][1]
            self.current_window.video = self.storage["video"]
            # self.current_window.load_win_state()
            self._panel.value = self.current_window
        else:
            return


if __name__ == '__main__':
    from pyforms import start_app

    start_app(MainWindow)
