import music21
from PyQt5 import QtWidgets


class UIClef(QtWidgets.QGraphicsItem):

    def __init__(self, baseline, *args, **kwargs):
        super(UIClef, self).__init__(*args, **kwargs)
        self.__baseline = baseline

    def position(self, pitch: music21.pitch.Pitch):
        """
        Return the line index of the given pitch relative to the lowest staff
        line in this clef.

        :param pitch: Pitch whose position is being checked

        :return:
          An integer, the number of lines above or below the lowest staff line of this clef
        """
        base_pitchnum = ord(str(self.__baseline)[0])
        pitchnum = ord(str(pitch)[0])
        base_octv = self.__baseline.implicitOctave
        octv = pitch.implicitOctave
        return 7 * (octv - base_octv) + (pitchnum - base_pitchnum)


def treble():
    return UIClef(music21.pitch.Pitch('E4'))
