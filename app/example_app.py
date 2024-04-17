from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlFile
from pyforms.controls import ControlText
from pyforms.controls import ControlSlider
from pyforms.controls import ControlPlayer
from pyforms.controls import ControlButton

import cv2
import numpy as np


class ComputerVisionAlgorithm(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__('Computer vision algorithm example')

        self.points_to_draw = []
        self.draw_lines = False

        # Definition of the forms fields
        self._videofile = ControlFile('Video')
        self._outputfile = ControlText('Results output file')
        self._threshold = ControlSlider('Threshold', default=114, minimum=0, maximum=255)
        self._blobsize = ControlSlider('Minimum blob size', default=110, minimum=100, maximum=2000)
        self._player = ControlPlayer('Player')
        self._runbutton = ControlButton('Run')

        # Define the function that will be called when a file is selected
        self._videofile.changed_event = self.__videoFileSelectionEvent
        # Define the event that will be called when the run button is processed
        self._runbutton.value = self.__runEvent
        # Define the event called before showing the image in the player
        self._player.process_frame_event = self.__process_frame

        self._player.click_event = self.__clickOnPlayerEvent

        self._player.key_press_event = self.__enterKeyPressEvent

        # Define the organization of the Form Controls
        self._formset = [
            ('_videofile', '_outputfile'),
            '_threshold',
            ('_blobsize', '_runbutton'),
            '_player'
        ]

    def __videoFileSelectionEvent(self):
        """
        When the videofile is selected instanciate the video in the player
        """
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

    def __runEvent(self):
        """
        After setting the best parameters run the full algorithm
        """
        pass

    def __clickOnPlayerEvent(self, event, x, y):
        self.points_to_draw += [[int(x), int(y)]]
        self._player.process_frame_event(self._player.frame)
        self._player.refresh()
        return event, x, y

    def __enterKeyPressEvent(self, event):
        if event.key() == 16777220 and len(self.points_to_draw) >= 3:
            print(event.key())
            self.draw_lines = True
            self._player.process_frame_event(self._player.frame)
            self._player.refresh()

        return event


if __name__ == '__main__':
    from pyforms import start_app

    start_app(ComputerVisionAlgorithm)
