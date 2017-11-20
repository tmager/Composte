
from PyQt5 import QtWidgets
from client.gui import UISettings

class UIMeasure(QtWidgets.QGraphicsItemGroup):

    def __init__(self, width, inh_clef, inh_keysig, inh_timesig,
                 *args, **kwargs):
        super(UIMeasure, self).__init__(args, kwargs)
        self.__width = width

        self.__clef = None
        self.__keysig = None
        self.__timesig = None

        self.__inherited_clef = inh_clef
        self.__inherited_keysig = inh_keysig
        self.__inherited_timesig = inh_timesig

        self.__baseObjs = []
        self.__noteObjs = {}

        self.__initGraphics()

        if self.__clef is not None:
            pass
        if self.__keysig is not None:
            pass
        if self.__timesig is not None:
            pass

    def __initGraphics(self):
        for i in range(0,4):
            line = QGraphicsLineItem(0, i * UISettings.STAFF_LINE_SEP,
                                     width, i * UISettings.STAFF_LINE_SEP,
                                     self)
            self.__baseObjs.append(line)
            self.addToGroup(line)

        barline = QGraphicsLineItem(0, 0, 0, 5 * UISettings.STAFF_LINE_SEP)
        self.__baseObjs.append(barline)
        self.addToGroup(barline)
        barline = QGraphicsLineItem(width, 0, width,
                                    5 * UISettings.STAFF_LINE_SEP)
        self.__baseObjs.append(barline)
        self.addToGroup(barline)

    def addNote(self, pitch, ntype, offset):
        note = ntype(parent = self)
        if offset + note.length():
            raise ValueError("Note extends past end of measure")
        if (pitch, ntype, offset) in self__noteObjs:
            raise ValueError("Note already exists")
        self.__noteObjs[(pitch, ntype, offset)] = note
        self.addToGroup(note)

    def delNote(self, pitch, ntype, offset):
        if (pitch, ntype, offset) not in self.__noteObjs:
            raise ValueError("Deleting nonexistent note")
        self.removeFromGroup(self.__noteObjs[(pitch, ntype, offset)])
        del self.__noteObjs[(pitch, ntype, offset)]
