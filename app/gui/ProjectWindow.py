import logging
import pathlib

from confapp import conf
from PyQt5 import QtWidgets

from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlDir
from pyforms.controls import ControlList
from pyforms.controls import ControlButton
from pyforms.controls import ControlCombo
from pyforms.controls import ControlLabel


class ProjectWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Настройка проекта')
        self.logger = logging.getLogger(__name__)

        self._project_dir = ControlDir("Папка проекта")
        self._project_dir.value = str(conf.CURRENT_PROJECT_DIR) if conf.CURRENT_PROJECT_DIR else str(conf.DEFAULT_PROJECT_DIR)
        self._project_dir.changed_event = self.__dirSelectionEvent

        self._video_list = ControlList("Список видео")
        self._video_list.readonly = True
        for file in conf.PROJECT_VIDEO_FILES.keys():
            self._video_list.__add__([file])
        self._video_list.item_selection_changed_event = self.__videoSelectionEvent

        self._files_sel_button = ControlButton("Добавить видео")
        self._files_sel_button.value = self.__fileSelectionEvent

        self._video_label = ControlLabel("Текущее видео: ")

        self._video_preproc = ControlCombo("Предобработка")
        self._video_tracking = ControlCombo("Трекинг")
        self._video_roi = ControlCombo("Области интереса")

        self.formset = (
            [
                '_project_dir',
                '_video_list',
                '_files_sel_button'
            ],
            "||",
            [
                ' ',
                '_video_label',
                '_video_preproc',
                '_video_tracking',
                '_video_roi',
                ' ',
                ' ',
                ' '
            ]
        )

    def __dirSelectionEvent(self):
        conf.CURRENT_PROJECT_DIR = pathlib.Path(self._project_dir.value)

    def __videoSelectionEvent(self):
        self._video_label.value = f"Текущее видео: {self._video_list.get_currentrow_value()[0]}"
        # current_video = conf.PROJECT_VIDEO_FILES[self._video_label.value]

    def __fileSelectionEvent(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filter = "Video files(*.avi)"
        fileNames, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                              "Open Files", "",
                                                              filter=filter,
                                                              options=options)
        if fileNames:
            for file in fileNames:
                path = pathlib.Path(file)
                conf.PROJECT_VIDEO_FILES[path.name] = {
                    "fpath": path,
                    "preprocessing": None,
                    "tracking": None,
                    "roi": None
                }
                self._video_list.__add__([path.name])


if __name__ == '__main__':
    from pyforms import start_app
    from confapp import conf
    import settings

    conf += settings

    start_app(ProjectWindow)
