from PyQt5 import QtWidgets

class UITimeSignature(QtWidgets.QGraphicsItem):

    def __init__(self, num, den, *args, **kwargs):
        super(UITimeSignature, self).__init__(*args, **kwargs)
        self.__num = num
        self.__den = den

    def measureLength(self):
        return 4 * self.__num / self.__den
