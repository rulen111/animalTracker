import logging

from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlDir
from pyforms.controls import ControlList
from pyforms.controls import ControlButton
from pyforms.controls import ControlCombo


class ProjectWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        BaseWidget.__init__(self, 'Настройка проекта')
        self.logger = logging.getLogger(__name__)

        self.project_dir = ControlDir("Папка проекта")
        self.video_list = ControlList()
        self.video_sel_button = ControlButton()
        self.video_preproc = ControlCombo()
        self.video_tracking = ControlCombo()
        self.video_roi = ControlCombo()

        self.formset = (
            [
                'project_dir',
                'video_sel_button',
                'video_list'
            ],
            "||",
            [
                'video_preproc',
                'video_tracking',
                'video_roi'
            ]
        )


if __name__ == '__main__':
    from pyforms import start_app

    start_app(ProjectWindow)
