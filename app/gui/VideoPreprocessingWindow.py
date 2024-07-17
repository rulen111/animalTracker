import pickle
import pathlib

from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlFile
from pyforms.controls import ControlText
from pyforms.controls import ControlNumber
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlCombo

import cv2
import numpy as np

from app.gui.controls.VideoPlayer import VideoPlayer
from app.cli.preprocessing import Preprocessing
from app.cli.video import Video
from app.gui.PreviewWindow import PreviewWindow

CONFIG_FILE_PATH = '../config.ini'
OBJECT_FILE_PATH = "../session.atr"


class VideoPreprocessingWindow(Preprocessing, BaseWidget):

    def __init__(self, *args, **kwargs):
        Preprocessing.__init__(self, *args, **kwargs)
        BaseWidget.__init__(self, 'Предварительная подготовка видео')
        # self.logger = logging.getLogger(__name__)

        self.video = kwargs.get("video", None)
        self.points_to_draw = kwargs.get("points_to_draw", [])
        self.draw_lines = kwargs.get("draw_lines", False)

        self._selvideo = ControlCombo('Текущее видео')
        self._selvideo.add_item("Загрузить новое видео")
        # for file in conf.PROJECT_VIDEO_FILES.keys():
        #     self._selvideo.add_item(file)

        self._videofile = ControlFile('Видео')
        videofile = kwargs.get("_videofile.value", None)
        if videofile:
            self._videofile.value = videofile
        self._videofile.changed_event = self.__videoFileSelectionEvent

        self._trstart = ControlText('Начало', default=str(kwargs.get("_trstart.value", 0)))
        self._trstart.changed_event = self.__trstartChangeEvent

        self._trend = ControlText('Конец', default=str(kwargs.get("_trend.value", 0)))
        self._trend.changed_event = self.__trendChangeEvent

        self._videores = ControlNumber(label='Resolution, %', default=kwargs.get("_videores.value", 100),
                                       minimum=0, maximum=100)
        self._videores.changed_event = self.__videoresChangeEvent

        self._chckmask = ControlCheckBox('Задать маску')
        self._chckmask.value = kwargs.get("_chckmask.value", self.mask.any())
        self._chckmask.changed_event = self.__chckmaskChangedEvent

        self._player = VideoPlayer()
        self._player.value = self._videofile.value
        self._player.process_frame_event = self.__process_frame
        self._player.click_event = self.__clickOnPlayerEvent
        self._player.key_press_event = self.__enterKeyPressEvent

        self._previewbutton = ControlButton('Предпросмотр')
        self._previewbutton.value = self.__previewEvent

        self._formset = (
            [
                ' ',
                '_selvideo',
                '_videofile',
                ' ',
                '_trstart',
                '_trend',
                '_videores',
                ' ',
                '_chckmask',
                '_previewbutton',
                ' '
            ],
            "||",
            '_player'
        )

        self.load_win_state()

    def save_win_state(self):
        if self.video:
            self.video.save(OBJECT_FILE_PATH)
        self.save(OBJECT_FILE_PATH)

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                temp = pickle.load(f)
        else:
            temp = {}

        temp.update({
            "VPWin": {
                "WindowState": self.save_form(),
                "Geometry": self.saveGeometry(),
                "points_to_draw": self.points_to_draw if self.points_to_draw else "empty",
                "draw_lines": 1 if self.draw_lines else 0,
            },
        })

        with open(OBJECT_FILE_PATH, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_win_state(self):
        if self.video:
            self.video.load(OBJECT_FILE_PATH)
            self.__videoFileSelectionEvent()
        self.load(OBJECT_FILE_PATH)

        if pathlib.Path(OBJECT_FILE_PATH).exists():
            with open(OBJECT_FILE_PATH, "rb") as f:
                entries = pickle.load(f)
        else:
            return

        session = entries.get("VPWin", {})

        state = session.get('WindowState', None)
        if state:
            self.load_form(state)

        geometry = session.get('Geometry', None)
        if geometry:
            self.restoreGeometry(geometry)

        self.points_to_draw = session.get("points_to_draw", [])
        self.points_to_draw = [] if self.points_to_draw == "empty" else self.points_to_draw
        self.draw_lines = bool(int(session.get("draw_lines", 0)))

    def __videoFileSelectionEvent(self):
        """
        When the videofile is selected instanciate the video in the player
        """
        self.video = Video(fpath=self._videofile.value)
        self.tracking_interval = [0, self.video.frame_cnt]
        self._player.value = self._videofile.value
        self._trend.value = str(self.tracking_interval[1])

    def __process_frame(self, frame):
        """
        Do some processing to the frame and return the result frame
        """
        if self.points_to_draw:
            for point in self.points_to_draw:
                x = point[0]
                y = point[1]
                frame = cv2.circle(frame, (x, y), radius=15, color=(0, 0, 255), thickness=-1)

        if self.draw_lines:
            points = np.array(self.points_to_draw)
            frame = cv2.polylines(frame, [points], True, (0, 0, 255))

        return frame

    def __previewEvent(self):
        """
        After setting the best parameters run the full algorithm
        """
        frame = self.preprocess_frame(self._player.frame)
        win = PreviewWindow(frame=frame)
        win.parent = self
        win.show()

    def __clickOnPlayerEvent(self, event, x, y):
        if self._chckmask.value:
            self.points_to_draw += [[int(x), int(y)]]
            self._player.process_frame_event(self._player.frame)
            self._player.refresh()
            return event, x, y
        else:
            return event, x, y

    def __enterKeyPressEvent(self, event):
        if event.key() == 16777220 and len(self.points_to_draw) >= 3:
            self.draw_lines = True
            self.generate_mask(self.points_to_draw, self.video.shape)
            self._player.refresh()

        return event

    def __trstartChangeEvent(self):
        self.tracking_interval[0] = int(self._trstart.value)

    def __trendChangeEvent(self):
        self.tracking_interval[1] = int(self._trend.value)

    def __videoresChangeEvent(self):
        self.resolution = self._videores.value / 100

    def __chckmaskChangedEvent(self):
        if self._chckmask.value:
            pass
        else:
            self.draw_lines = False
            self.points_to_draw = []
            self.mask = np.array([])
            self._player.refresh()

    def closeEvent(self, event):
        self.save_win_state()
        super().closeEvent(event)


if __name__ == '__main__':
    from pyforms import start_app
    from confapp import conf
    import settings

    conf += settings

    start_app(VideoPreprocessingWindow)
