import music21

from PyQt5 import QtWidgets

class UITimeSignature(QtWidgets.QGraphicsItem):

    def __init__(self, num, den, *args, **kwargs):
        super(UITimeSignature, self).__init__(*args, **kwargs)
        self.__num = num
        self.__den = den

    def __eq__(self, ts):
        return self.__num == ts.__num and self.__den == ts.__den

    def measureLength(self):
        return 4 * self.__num / self.__den

# END class UITimeSignature

def fromMusic21(ts: music21.meter.TimeSignature):
    return UITimeSignature(ts.numerator, ts.denominator)
