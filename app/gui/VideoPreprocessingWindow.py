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

from app.src.video import Video
from app.gui.PreviewWindow import PreviewWindow


CONFIG_FILE_PATH = '../config.ini'


class VideoPreprocessingWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        # Video.__init__(self)
        BaseWidget.__init__(self, 'Предварительная подготовка видео')
        self.logger = logging.getLogger(__name__)

        self.video = Video()
        # self.video = vid
        self.points_to_draw = []
        self.draw_lines = False

        # Definition of the forms fields
        self._videofile = ControlFile('Video')
        self._trstart = ControlText('Start')
        self._trend = ControlText('End')
        self._videores = ControlNumber(label='Resolution, %', default=100, minimum=0, maximum=100)
        self._chckmask = ControlCheckBox('Define mask')
        self._player = ControlPlayer('Player')
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
        self._formset = [
            ('_videofile', '_videores'),
            ('_trstart', '_trend', '_chckmask'),
            '_previewbutton',
            '_player'
        ]

    def __getstate__(self):
        state = {
            "video": self.video,
            "points_to_draw": self.points_to_draw,
            "draw_lines": self.draw_lines
        }
        return state

    def __save_video(self):
        return self.video

    def save_win_state(self):
        settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)
        settings.setValue('VPWin/WindowState', self.save_form())
        settings.setValue('VPWin/Geometry', self.saveGeometry())

    def load_win_state(self):
        settings = QSettings(CONFIG_FILE_PATH, QSettings.IniFormat)

        state = settings.value('VPWin/WindowState')
        if state:
            self.load_form(state)

        geometry = settings.value('VPWin/Geometry')
        if geometry:
            self.restoreGeometry(geometry)

    def __videoFileSelectionEvent(self):
        """
        When the videofile is selected instanciate the video in the player
        """
        self.video.load_video(self._videofile.value)
        self.points_to_draw = []
        self.draw_lines = False
        self._player.value = self._videofile.value

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

        frame = self.video.preprocess_frame(self._player.frame)
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
            self.video.generate_mask(self.points_to_draw)
            # self._player.process_frame_event(self._player.frame)
            self._player.refresh()

        return event

    def __trstartChangeEvent(self):
        self.video.tr_range[0] = int(self._trstart.value)

    def __trendChangeEvent(self):
        self.video.tr_range[1] = int(self._trend.value)

    def __videoresChangeEvent(self):
        self.video.dsmpl = self._videores.value / 100

    def __chckmaskChangedEvent(self):
        if self._chckmask.value:
            pass
        else:
            self.draw_lines = False
            self.points_to_draw = []
            self.video.mask = np.array([])
            self._player.refresh()


if __name__ == '__main__':
    from pyforms import start_app

    start_app(VideoPreprocessingWindow)
