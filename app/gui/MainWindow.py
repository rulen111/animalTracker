import pathlib
import pickle

from PyQt5.QtCore import QSettings
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlList
from pyforms.controls import ControlButton

from app.gui.ArenaROIWindow import ArenaROIWindow
from app.gui.EditTrackWindow import EditTrackWindow
from app.gui.TrackingWindow import TrackingWindow
from app.gui.VideoPreprocessingWindow import VideoPreprocessingWindow

CONFIG_FILE_PATH = '../config.ini'
OBJECT_FILE_PATH = "../session.atr"


class MainWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Animal Tracker')
        # self.logger = logging.getLogger(__name__)

        self.reached = 0 if "reached" not in kwargs.keys() else kwargs["reached"]

        self.current_window_idx = 0 if "current_window_idx" not in kwargs.keys() else kwargs["current_window_idx"]
        self.windows = {
            0: ["Предварительная подготовка видео", VideoPreprocessingWindow],
            1: ["Настройка трекинг", TrackingWindow],
            2: ["Редактор трека", EditTrackWindow],
            3: ["Области интереса", ArenaROIWindow]
        } if "windows" not in kwargs.keys() else kwargs["windows"]

        self._current_window = self.windows[self.current_window_idx][1]()
        self._current_window.parent = self

        self._panel = ControlEmptyWidget()
        self._panel.value = self._current_window

        self._winlist = ControlList("Разделы")
        for idx, window in self.windows.items():
            self._winlist.__add__([window[0]])
        self._winlist.readonly = True

        self._nextbutton = ControlButton("Далее")
        self._nextbutton.value = self.__nextWindowEvent

        self._backbutton = ControlButton("Назад")
        self._backbutton.value = self.__prevWindowEvent

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

        self.load_win_state()

        # self.mainmenu = [
        #     {'File': [
        #         {"Open": self.__open},
        #         {'Save as': self.__save_as}
        #     ]
        #     }
        # ]

    # def __save_as(self):  # TODO
    #     options = QtWidgets.QFileDialog.Options()
    #     options |= QtWidgets.QFileDialog.DontUseNativeDialog
    #     filter = "Animal Tracker Project(*.atpr)"
    #     fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,
    #                                                         "Save File", "",
    #                                                         filter=filter,
    #                                                         options=options)
    #
    #     # self.session.save_to_file(fileName)
    #     if fileName:
    #         fpath = fileName.split(".")
    #         fpath = fpath[0]
    #         with open(fpath + ".atpr", 'wb') as f:
    #             # data = self.__dict__
    #             # data.pop("_mainmenu")
    #             # print(data.keys())
    #             # print(data.values())
    #             try:
    #                 # print(self.session.__getstate__())
    #                 pickle.dump(self.session.__getstate__(), f, pickle.HIGHEST_PROTOCOL)
    #             except Exception as e:
    #                 print(e)
    #
    # def __open(self):  # TODO
    #     options = QtWidgets.QFileDialog.Options()
    #     options |= QtWidgets.QFileDialog.DontUseNativeDialog
    #     filter = "Animal Tracker Project(*.atpr)"
    #     fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
    #                                                         "Open File", "",
    #                                                         filter=filter,
    #                                                         options=options)
    #
    #     # self.session.load_from_file(fileName)
    #     # self.current_window = self.session.windows[self.session.current_window_idx][1]
    #     # self.current_window.parent = self
    #     # self._panel.value = self.current_window
    #     if fileName:
    #         with open(fileName, 'rb') as f:
    #             try:
    #                 # self.session = pickle.load(f)
    #                 state = pickle.load(f)
    #                 # print(state)
    #                 self.session.__setstate__(state)
    #                 # self.__dict__.update(state)
    #                 # self.__setstate__(state)
    #                 self._current_window = self.session.windows[self.session.current_window_idx][1]
    #                 self._current_window.parent = self
    #                 self._panel.value = self._current_window
    #             except Exception as e:
    #                 print(e)

    def save_win_state(self):
        # session = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        #
        # session.setValue('MainWin/WindowState', self.save_form())
        # session.setValue('MainWin/Geometry', self.saveGeometry())

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                temp = pickle.load(f)
        else:
            temp = {}

        temp.update({
            "MainWin": {
                "WindowState": self.save_form(),
                "Geometry": self.saveGeometry(),
            },
        })

        with open(OBJECT_FILE_PATH, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_win_state(self):
        # session = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        #
        # state = session.value('MainWin/WindowState')
        # if state:
        #     self.load_form(state)
        #
        # geometry = session.value('MainWin/Geometry')
        # if geometry:
        #     self.restoreGeometry(geometry)

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                entries = pickle.load(f)
        else:
            return

        session = entries.get("MainWin", {})

        state = session.get('WindowState', None)
        if state:
            self.load_form(state)

        geometry = session.get('Geometry', None)
        if geometry:
            self.restoreGeometry(geometry)

    def __nextWindowEvent(self):
        if self.current_window_idx < (len(self.windows.keys()) - 1):
            self._current_window.close()
            self.current_window_idx += 1

            self._current_window = self.windows[self.current_window_idx][1]()
            self._current_window.parent = self

            self._panel.value = self._current_window

    def __prevWindowEvent(self):
        if self.current_window_idx > 0:
            self._current_window.close()
            self.current_window_idx -= 1

            self._current_window = self.windows[self.current_window_idx][1]()
            self._current_window.parent = self

            self._panel.value = self._current_window

    def closeEvent(self, event):
        self.save_win_state()
        super().closeEvent(event)


if __name__ == '__main__':
    from pyforms import start_app
    from confapp import conf
    import settings

    conf += settings

    start_app(MainWindow)
