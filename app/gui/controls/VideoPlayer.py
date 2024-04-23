from pyforms.controls import ControlPlayer


class VideoPlayer(ControlPlayer):

    def __init__(self, *args, **kwargs):
        ControlPlayer.__init__(self, *args, **kwargs)

    def videoProgress_valueChanged(self):
        milli = self._value.get(0)
        (minutes, seconds, milliseconds) = self.convertFrameToTime(milli)
        self.videoTime.setText(
            "%02d:%02d:%03d" % (minutes, seconds, milliseconds))

        if not self.is_playing and self._update_video_slider:
            new_index = self.videoProgress.value()
            self._value.set(1, new_index)
            self.call_next_frame(update_slider=False, increment_frame=False)
