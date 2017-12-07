
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsLineItem
from client.gui import UISettings
from client.gui.UINote import UINote

import music21

class UIMeasure(QtWidgets.QGraphicsItemGroup):

    __stafflineWidth = 1
    __barlineWidth = 2
    __stafflinePen = QtGui.QPen(QtGui.QBrush(Qt.black),
                                __stafflineWidth,
                                Qt.SolidLine, Qt.FlatCap)
    __barlinePen = QtGui.QPen(QtGui.QBrush(Qt.black),
                              __barlineWidth,
                              Qt.SolidLine, Qt.FlatCap)

    def __init__(self, scene, width, clef, keysig, timesig,
                 newClef = False, newKeysig = False, newTimesig = False,
                 forceDrawClef = False, *args, **kwargs):
        super(UIMeasure, self).__init__(*args, **kwargs)
        self.__scene = scene
        self.__width = width

        self.__clef = clef
        self.__newClef = False
        self.__keysig = keysig
        self.__newKeysig = False
        self.__timesig = timesig
        self.__newTimesig = False

        self.__baseObjs = []
        self.__noteObjs = {}

        self.__initGraphics()

    def __initGraphics(self):
        for i in range(0,5):
            line = QGraphicsLineItem(0, 2 * i * UISettings.PITCH_LINE_SEP,
                                     self.__width,
                                     2 * i * UISettings.PITCH_LINE_SEP,
                                     self)
            line.setPen(self.__stafflinePen)
            self.__baseObjs.append(line)

        barline_y1 = -self.__stafflineWidth/2
        barline_y2 = 4 * 2 * UISettings.PITCH_LINE_SEP + self.__stafflineWidth/2

        barline = QGraphicsLineItem(0, barline_y1,
                                    0, barline_y2,
                                    parent=self)
        barline.setPen(self.__barlinePen)
        self.__baseObjs.append(barline)
        barline = QGraphicsLineItem(self.__width, barline_y1,
                                    self.__width, barline_y2,
                                    parent = self)
        barline.setPen(self.__barlinePen)
        self.__baseObjs.append(barline)

    def clear(self):
        for item in self.__noteObjs.values():
            self.__scene.removeItem(item)
        self.__noteObjs.clear()
        for item in self.__baseObjs:
            self.__scene.removeItem(item)
        self.__baseObjs.clear()
        self.__initGraphics()

    def __redraw(self):
        """
        Redraw all graphics objects, moving them to update as necessary, e.g.
        after a resize.
        """
        ## TODO: This is a terrible way of doing this, we could reuse the old
        ##   objects rather than destroying them and creating new ones.
        notes = list(self.__noteObjs.keys())
        self.clear()

        self.__initGraphics()
        for note in notes:
            self.addNote(*note)

    def insertNote(self, pitch: music21.pitch.Pitch, ntype, offset: float):
        note = ntype(pitch, self.__clef, self.__keysig, parent = self)
        if offset + note.length() > self.length():
            raise ValueError("Note extends past end of measure")
        if (pitch, ntype, offset) in self.__noteObjs:
            raise ValueError("Note already exists")
        self.__noteObjs[(pitch, ntype, offset)] = note

        notesWidth = (self.__width
                        - UISettings.BARLINE_FRONT_PAD
                        - UISettings.BARLINE_REAR_PAD )
        note_x = (UISettings.BARLINE_FRONT_PAD
                    + notesWidth * (offset / (self.length() - 1)))
        note_y = 0 #(8 * UISettings.PITCH_LINE_SEP
                   # - self.clef().position(pitch) * UISettings.PITCH_LINE_SEP)
        note.setPos(note_x, note_y)


    def deleteNote(self, pitch: music21.pitch.Pitch, offset: float):
        for note in self.__noteObjs.keys():
            if note[0] == pitch and note[2] == offset:
                self.__scene.removeItem(self.__noteObjs[note])
                del self.__noteObjs[note]
                return True
        return False

    def clef(self):
        return self.__clef
    def keysig(self):
        return self.__keysig
    def timesig(self):
        return self.__timesig
    def width(self):
        return self.__width

    def setClef(self, clef, newClef = True):
        self.__clef = clef
        self.__newClef = newClef
    def setKeysig(self, keysig, newKeysig = True):
        self.__keysig = keysig
        self.__newKeysig = newKeysig
    def setTimesig(self, timesig, newTimesig = True):
        self.__timesig = timesig
        self.__newTimesig = newTimesig
    def setWidth(self, width):
        self.__width = width
        self.__redraw()

    def length(self):
        return self.__timesig.measureLength()
