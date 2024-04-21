from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlImage


class PreviewWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__('Preview window')

        self._image = ControlImage()
        if 'frame' in kwargs.keys():
            self._image.value = kwargs['frame']

        self._formset = ['_image']


if __name__ == '__main__':
    from pyforms import start_app

    start_app(PreviewWindow)
