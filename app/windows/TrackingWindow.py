from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlCombo
from pyforms.controls import ControlPlayer
from pyforms.controls import ControlButton
from pyforms.controls import ControlSlider

from app.src.tracker import Tracker, save_outputv
from app.src.video import Video
from app.windows.PreviewWindow import PreviewWindow


class TrackingWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Настройка трекинга')

        self.video = Video()
        self.video.load_state("current_video.pckl")
        self.tracker = Tracker()

        self._selmethod = ControlCombo('Метод фона')
        for item in ["median", "mean", "max", "min"]:
            self._selmethod.add_item(item)
        self._player = ControlPlayer('Player')
        self._player.value = self.video.fpath
        self._previewbutton = ControlButton('Preview background')
        self._runbutton = ControlButton('Run tracking')
        self._threshold = ControlSlider(label='Threshold', default=995, minimum=0, maximum=1000)

        self._player.process_frame_event = self.__process_frame

        self._selmethod.changed_event = self.__bgmethodChangeEvent

        self._previewbutton.value = self.__previewEvent

        self._runbutton.value = self.__runEvent

        self._threshold.changed_event = self.__threshChangeEvent

        self._formset = [
            ('_selmethod', '_previewbutton'),
            '_threshold',
            '_player',
            '_runbutton'
        ]

    def __process_frame(self, frame):
        frame = self.video.preprocess_frame(frame)

        return frame

    def __bgmethodChangeEvent(self):
        self.video.bg_ref[0] = self._selmethod.value
        self.video.bg_ref[1] = None

    def __previewEvent(self):
        self.video.make_bg()
        self.video.save_state("current_video.pckl")

        frame = self.video.bg_ref[1]
        win = PreviewWindow(frame=frame)
        win.parent = self
        win.show()

    def __runEvent(self):
        self.tracker.params["bg_ref"] = self.video.bg_ref[1]
        self.tracker.params["thresh"] = self._threshold.value / 10
        df = self.tracker.do_tracking(self.video)
        print(df.head(20))
        save_outputv(self.video)
        self.video.save_state("current_video.pckl")

    def __threshChangeEvent(self):
        self.tracker.params["thresh"] = self._threshold.value / 10


if __name__ == '__main__':
    from pyforms import start_app

    start_app(TrackingWindow)
