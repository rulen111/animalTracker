import cv2
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlPlayer
from pyforms.controls import ControlTableView
from pyforms.controls import ControlImage
from pyforms.controls import ControlSlider


from app.src.video import Video
from app.windows.models.TableModel import TableModel


def draw_track(frame, points):
    for idx, point in enumerate(points):
        frame = cv2.circle(frame, (point[0], point[1]), radius=1, color=255, thickness=-1)

    return frame


class EditTrackWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Редактор трека')

        self.video = Video()
        self.video.load_state("current_video.pckl")

        data = [[f"{coords[0]:.6}", f"{coords[1]:.6}"]
                for coords in zip(self.video.track[0], self.video.track[1])]
        self._model = TableModel(data)

        self.cap = cv2.VideoCapture(self.video.fpath)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.video.tr_range[0])
        ret, frame = self.cap.read()
        frame = self.video.preprocess_frame(frame)
        self._frameimg = ControlImage()
        self._frameimg.value = frame

        self._frameslider = ControlSlider(default=1, minimum=1, maximum=len(self.video.track[0]))

        # self._player = ControlPlayer('Player')
        # self._player.value = self.video.fpath
        # self._player.value.set(cv2.CAP_PROP_POS_FRAMES, self.video.tr_range[0])

        self._coordtable = ControlTableView("Координаты")
        self._coordtable.setModel(self._model)

        self.closeEvent = self.__formClosedEvent
        self._frameslider.changed_event = self.__frameSelectionEvent

        self._formset = [
            (('_frameimg', ), '_coordtable'),
            '_frameslider'
        ]

    def __formClosedEvent(self, event):
        self.cap.release()
        return event

    def __frameSelectionEvent(self):
        current_frame = int(self._frameslider.value)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES,
                     self.video.tr_range[0] + (current_frame - 1)
                     )
        ret, frame = self.cap.read()
        frame = self.video.preprocess_frame(frame)
        points = [[int(coords[0]), int(coords[1])]
                  for coords in zip(self.video.track[0][:current_frame], self.video.track[1][:current_frame])
                  ]
        frame = draw_track(frame, points)
        self._frameimg.value = frame


if __name__ == '__main__':
    from pyforms import start_app

    start_app(EditTrackWindow)