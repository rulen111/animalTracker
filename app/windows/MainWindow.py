from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlList
from pyforms.controls import ControlButton

from app.windows.ArenaROIWindow import ArenaROIWindow
from app.windows.EditTrackWindow import EditTrackWindow
from app.windows.TrackingWindow import TrackingWindow
from app.windows.VideoPreprocessingWindow import VideoPreprocessingWindow


class MainWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Animal Tracker')

        # self.windows = [VideoPreprocessingWindow, TrackingWindow, EditTrackWindow, ArenaROIWindow]
        # self.windows = {
        #     "Предварительная подготовка видео": VideoPreprocessingWindow,
        #     "Настройка трекинг": TrackingWindow,
        #     "Редактор трека": EditTrackWindow,
        #     "Области интереса": ArenaROIWindow
        # }
        self.windows = {
            0: ("Предварительная подготовка видео", VideoPreprocessingWindow),
            1: ("Настройка трекинг", TrackingWindow),
            2: ("Редактор трека", EditTrackWindow),
            3: ("Области интереса", ArenaROIWindow)
        }
        self.current_window_idx = 0

        self._panel = ControlEmptyWidget()
        self.current_window = self.windows[self.current_window_idx][1]()
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

    def __nextWindowEvent(self):
        self.current_window_idx += 1
        self.current_window = self.windows[self.current_window_idx][1]()
        self._panel.value = self.current_window

    def __prevWindowEvent(self):
        self.current_window_idx -= 1
        self.current_window = self.windows[self.current_window_idx][1]()
        self._panel.value = self.current_window


if __name__ == '__main__':
    from pyforms import start_app

    start_app(MainWindow)
