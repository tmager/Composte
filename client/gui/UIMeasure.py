
from PyQt5 import QtWidgets
from client.gui import UISettings

class UIMeasure(QtWidgets.QGraphicsItemGroup):

    def __init__(self, width, clef, keysig, timesig,
                 newClef = False, newKeysig = False, newTimesig = False,
                 forceDrawClef = False, *args, **kwargs):
        super(UIMeasure, self).__init__(args, kwargs)
        self.__width = width

        self.__clef = clef
        self.__keysig = keysig
        self.__timesig = timesig

        self.__baseObjs = []
        self.__noteObjs = {}

        self.__initGraphics()

    def __initGraphics(self):
        for i in range(0,4):
            line = QGraphicsLineItem(0, 2 * i * UISettings.STAFF_LINE_SEP,
                                     width, 2 * i * UISettings.STAFF_LINE_SEP,
                                     self)
            self.__baseObjs.append(line)
            self.addToGroup(line)

        barline = QGraphicsLineItem(0, 0, 0, 5 * 2 * UISettings.STAFF_LINE_SEP)
        self.__baseObjs.append(barline)
        self.addToGroup(barline)
        barline = QGraphicsLineItem(width, 0, width,
                                    5 * 2 * UISettings.STAFF_LINE_SEP)
        self.__baseObjs.append(barline)
        self.addToGroup(barline)

    def addNote(self, pitch, ntype, offset):
        note = ntype(parent = self)
        if offset + note.length() > self.__inherited_timesig.measureLength():
            raise ValueError("Note extends past end of measure")
        if (pitch, ntype, offset) in self.__noteObjs:
            raise ValueError("Note already exists")
        self.__noteObjs[(pitch, ntype, offset)] = note
        self.addToGroup(note)

    def delNote(self, pitch, ntype, offset):
        if (pitch, ntype, offset) not in self.__noteObjs:
            raise ValueError("Deleting nonexistent note")
        self.removeFromGroup(self.__noteObjs[(pitch, ntype, offset)])
        del self.__noteObjs[(pitch, ntype, offset)]

    def length(self):
        return self.__timesig.measureLength()
