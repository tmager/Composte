import music21
from PyQt5 import QtWidgets


class UIClef(QtWidgets.QGraphicsItem):

    def __init__(self, baseline, *args, **kwargs):
        super(UIClef, self).__init__(*args, **kwargs)
        self.__baseline = baseline

    def __eq__(self, clef):
        return self.__baseline == clef.__baseline

    def position(self, pitch: music21.pitch.Pitch):
        """
        Return the line index of the given pitch relative to the lowest staff
        line in this clef.

        :param pitch: Pitch whose position is being checked

        :return: An integer, the number of lines above or below the lowest staff
                 line of this clef
        """
        return pitch.diatonicNoteNum - self.__baseline.diatonicNoteNum



def treble():
    return UIClef(music21.pitch.Pitch('E4'))


def fromMusic21(cl: music21.clef.Clef):
    if isinstance(cl, music21.clef.TrebleClef):
        return treble()
    else:
        raise RuntimeError('Unsupported clef ' + cl)
