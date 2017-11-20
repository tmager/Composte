import music21
from PyQt5 import QtWidgets


class UIClef(QtWidgets.QGraphicsItem):

    def __init__(self, baseline, *args, **kwargs):
        super(UIClef, self).__init__(*args, **kwargs)
        self.__baseline = baseline

    def position(self, note):
        base_pitch = ord(str(self.__baseline.pitch)[0])
        pitch = ord(str(note.pitch)[0])
        base_octv = self.__baseline.pitch.implicitOctave
        octv = note.pitch.implicitOctave
        print(pitch, base_pitch, octv, base_octv)
        return 8 * (octv - base_octv) + (pitch - base_pitch)
