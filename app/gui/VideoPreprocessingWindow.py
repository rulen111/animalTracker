import datetime

from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlFile
from pyforms.controls import ControlText
from pyforms.controls import ControlPlayer
from pyforms.controls import ControlNumber
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox

from PyQt5.QtCore import Qt, QSettings

import cv2
import numpy as np
import logging

from app.gui.controls.VideoPlayer import VideoPlayer
from app.src.video import Video
from app.gui.PreviewWindow import PreviewWindow


CONFIG_FILE_PATH = '../config.ini'


class VideoPreprocessingWindow(Video, BaseWidget):

    def __init__(self, *args, **kwargs):
        Video.__init__(self, *args, **kwargs)
        BaseWidget.__init__(self, 'Предварительная подготовка видео')
        self.logger = logging.getLogger(__name__)

        # self.video = Video()
        # self.video = vid
        self.points_to_draw = kwargs.get("points_to_draw", [])
        self.draw_lines = kwargs.get("draw_lines", False)

        # Definition of the forms fields
        self._videofile = ControlFile('Video')
        videofile = kwargs.get("_videofile.value", self.fpath)
        if videofile:
            self._videofile.value = videofile
        self._trstart = ControlText('Start', default=str(kwargs.get("_trstart.value", 0)))
        self._trend = ControlText('End', default=str(kwargs.get("_trend.value", 0)))
        self._videores = ControlNumber(label='Resolution, %', default=kwargs.get("_videores.value", 100),
                                       minimum=0, maximum=100)
        self._chckmask = ControlCheckBox('Define mask')
        self._chckmask.value = kwargs.get("_chckmask.value", np.any(self.mask))
        # self._player = ControlPlayer('Player')
        self._player = VideoPlayer()
        self._player.value = self._videofile.value
        self._previewbutton = ControlButton('Preview frame')

        # Define the function that will be called when a file is selected
        self._videofile.changed_event = self.__videoFileSelectionEvent
        # Define the event that will be called when the run button is processed
        self._previewbutton.value = self.__previewEvent
        # Define the event called before showing the image in the player
        self._player.process_frame_event = self.__process_frame

        self._player.click_event = self.__clickOnPlayerEvent

        self._player.key_press_event = self.__enterKeyPressEvent

        self._trstart.changed_event = self.__trstartChangeEvent
        self._trend.changed_event = self.__trendChangeEvent

        self._videores.changed_event = self.__videoresChangeEvent

        self._chckmask.changed_event = self.__chckmaskChangedEvent

        # Define the organization of the Form Controls
        # self._formset = [
        #     ('_videofile', " ", " ", " "),
        #     ('_trstart', '_videores', " ", " "),
        #     ('_trend', '_chckmask', " ", " "),
        #     ('_previewbutton', " ", " "),
        #     '_player'
        # ]
        self._formset = (
            [
                '_videofile',
                '_trstart',
                '_videores',
                '_trend',
                '_chckmask',
                '_previewbutton'
            ],
            "||",
            '_player'
        )

    def __getstate__(self):
        state = self.get_video_state()
        state["points_to_draw"] = self.points_to_draw
        state["draw_lines"] = self.draw_lines
        state["_videofile.value"] = self._videofile.value
        state["_trstart.value"] = self._trstart.value
        state["_trend.value"] = self._trend.value
        state["_videores.value"] = self._videores.value
        state["_chckmask.value"] = self._chckmask.value

        return state

    def __setstate__(self, state):
        self.init_video(**state)

        self.points_to_draw = state.get("points_to_draw", [])
        self.draw_lines = state.get("draw_lines", False)
        videofile = state.get("_videofile.value", self.fpath)
        if videofile:
            self._videofile.value = videofile
            self._player.value = self._videofile.value
        self._trstart.value = state.get("_trstart.value", 0)
        self._trend.value = state.get("_trend.value", 0)
        self._videores.value = state.get("_videores.value", 100)
        self._chckmask.value = state.get("_chckmask.value", np.any(self.mask))

    def init_video(self, *args, **kwargs):
        # for key, value in kwargs.items():
        #     if key in self.__dict__.keys():
        #         self.__dict__[key] = value
        self.__dict__.update(kwargs)

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

    # def __save_video(self):
    #     return self.video
    #
    # def save_win_state(self):
    #     settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
    #     settings.setValue('VPWin/WindowState', self.save_form())
    #     settings.setValue('VPWin/Geometry', self.saveGeometry())
    #
    # def load_win_state(self):
    #     settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
    #
    #     state = settings.value('VPWin/WindowState')
    #     if state:
    #         self.load_form(state)
    #
    #     geometry = settings.value('VPWin/Geometry')
    #     if geometry:
    #         self.restoreGeometry(geometry)

    def __videoFileSelectionEvent(self):
        """
        When the videofile is selected instanciate the video in the player
        """
        Video.__init__(self, fpath=self._videofile.value)
        self._player.value = self._videofile.value
        self._trend.value = str(self.tr_range[1])

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
            # frame = cv2.fillPoly(frame, [points], (0, 0, 255))

        return frame

    def __previewEvent(self):
        """
        After setting the best parameters run the full algorithm
        """
        # super().save_state(f"{self.fname}.pckl")
        # self.video.save_state("app/gui/current_video.pckl")

        # frame = self.video.preprocess_frame(self._player.frame)
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
            # self.video.generate_mask(self.points_to_draw)
            self.generate_mask(self.points_to_draw)
            # self._player.process_frame_event(self._player.frame)
            self._player.refresh()

        return event

    def __trstartChangeEvent(self):
        # self.video.tr_range[0] = int(self._trstart.value)
        self.tr_range[0] = int(self._trstart.value)

    def __trendChangeEvent(self):
        # self.video.tr_range[1] = int(self._trend.value)
        self.tr_range[1] = int(self._trend.value)

    def __videoresChangeEvent(self):
        # self.video.dsmpl = self._videores.value / 100
        self.dsmpl = self._videores.value / 100

    def __chckmaskChangedEvent(self):
        if self._chckmask.value:
            pass
        else:
            self.draw_lines = False
            self.points_to_draw = []
            # self.video.mask = np.array([])
            self.mask = np.array([])
            self._player.refresh()


if __name__ == '__main__':
    from pyforms import start_app

    start_app(VideoPreprocessingWindow)
