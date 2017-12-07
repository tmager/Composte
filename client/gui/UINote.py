import music21

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt

from util.classExceptions import virtualmethod
import client.gui.UISettings as UISet


def ntypeFromMusic21(note: music21.note.Note):
    ntypeMap = {
        'quarter' : UINote_Quarter,
        'half'    : UINote_Half,
        'whole'   : UINote_Whole
    }
    if note.duration.type in ntypeMap:
        return ntypeMap[note.duration.type]
    else:
        raise RuntimeError('Unsupported note duration ' + note.duration)

class UINote(QtWidgets.QGraphicsItem):

    __accidentalLineWidth = 1.5
    __accidentalPen = QtGui.QPen(QtGui.QColor(0,0,0),
                                 __accidentalLineWidth,
                                 Qt.SolidLine, Qt.FlatCap)
    __accidentalBrush = QtGui.QBrush(Qt.NoBrush)

    def __init__(self, pitch, clef, keysig, *args, **kwargs):
        super(UINote, self).__init__(*args, **kwargs)
        self.__pitch = pitch
        self.__clef = clef
        self.__keysig = keysig

        self._yoffset = (8 * UISet.PITCH_LINE_SEP
                          - self.__clef.position(pitch) * UISet.PITCH_LINE_SEP)


    @virtualmethod
    def length(self):
        """
        Return the length of the note, in quarter note increments.
        """

    def boundingRect(self):
        """
        Return a rectangle enclosing the entire drawn object.
        """
        y = self._yoffset
        return QtCore.QRectF(-3.5 * UISet.PITCH_LINE_SEP - 5,
                             y - 7 * UISet.PITCH_LINE_SEP,
                             4.75 * UISet.PITCH_LINE_SEP + 10,
                             9 * UISet.PITCH_LINE_SEP + 10)


    def _paintAccidental(self, painter, option, widget):
        y = self._yoffset
        painter.setPen(self.__accidentalPen)
        painter.setBrush(self.__accidentalBrush)
        if self.__keysig.accidentalMarkOf(self.__pitch) is None:
            return
        elif self.__keysig.accidentalMarkOf(self.__pitch).name == 'flat':
            path = QtGui.QPainterPath()
            path.moveTo(UISet.ACCIDENTAL_X_OFFSET + 0.5,
                        y - 3.3 * UISet.PITCH_LINE_SEP
                                                  + UISet.ACCIDENTAL_Y_OFFSET)
            path.lineTo(UISet.ACCIDENTAL_X_OFFSET + 0.5,
                        y + 1.2 * UISet.PITCH_LINE_SEP
                                                  + UISet.ACCIDENTAL_Y_OFFSET)
            path.quadTo(0.25 * UISet.ACCIDENTAL_X_OFFSET + 0.5,
                        y - 0.8 * UISet.PITCH_LINE_SEP
                                                  + UISet.ACCIDENTAL_Y_OFFSET,
                        UISet.ACCIDENTAL_X_OFFSET + 0.5,
                        y - 0.6 * UISet.PITCH_LINE_SEP
                                                  + UISet.ACCIDENTAL_Y_OFFSET)
            painter.drawPath(path)
        elif self.__keysig.accidentalMarkOf(self.__pitch).name == 'natural':
            painter.drawLine(UISet.ACCIDENTAL_X_OFFSET
                                                + 0.5 * UISet.PITCH_LINE_SEP,
                             y - 2 * UISet.PITCH_LINE_SEP,
                             UISet.ACCIDENTAL_X_OFFSET
                                                + 0.5 * UISet.PITCH_LINE_SEP,
                             y + 1.1 * UISet.PITCH_LINE_SEP)
            painter.drawLine(UISet.ACCIDENTAL_X_OFFSET
                                                + 1.25 * UISet.PITCH_LINE_SEP,
                             y - 1.1 * UISet.PITCH_LINE_SEP,
                             UISet.ACCIDENTAL_X_OFFSET
                                                + 1.25 * UISet.PITCH_LINE_SEP,
                             y + 2 * UISet.PITCH_LINE_SEP)
            painter.drawLine(UISet.ACCIDENTAL_X_OFFSET
                                                + 0.5 * UISet.PITCH_LINE_SEP,
                             y - 0.5 * UISet.PITCH_LINE_SEP,
                             UISet.ACCIDENTAL_X_OFFSET
                                                + 1.25 * UISet.PITCH_LINE_SEP,
                             y - 1 * UISet.PITCH_LINE_SEP)
            painter.drawLine(UISet.ACCIDENTAL_X_OFFSET
                                                + 0.5 * UISet.PITCH_LINE_SEP,
                             y + 1 * UISet.PITCH_LINE_SEP,
                             UISet.ACCIDENTAL_X_OFFSET
                                                + 1.25 * UISet.PITCH_LINE_SEP,
                             y + 0.5 * UISet.PITCH_LINE_SEP)

        elif self.__keysig.accidentalMarkOf(self.__pitch).name == 'sharp':
            painter.drawLine(UISet.ACCIDENTAL_X_OFFSET
                                                + 0.5 * UISet.PITCH_LINE_SEP,
                             y - 2 * UISet.PITCH_LINE_SEP,
                             UISet.ACCIDENTAL_X_OFFSET
                                                + 0.5 * UISet.PITCH_LINE_SEP,
                             y + 2.5 * UISet.PITCH_LINE_SEP)
            painter.drawLine(UISet.ACCIDENTAL_X_OFFSET
                                                + 1.25 * UISet.PITCH_LINE_SEP,
                             y - 2.5 * UISet.PITCH_LINE_SEP,
                             UISet.ACCIDENTAL_X_OFFSET
                                                + 1.25 * UISet.PITCH_LINE_SEP,
                             y + 2 * UISet.PITCH_LINE_SEP)
            painter.drawLine(UISet.ACCIDENTAL_X_OFFSET,
                             y - 0.5 * UISet.PITCH_LINE_SEP,
                             UISet.ACCIDENTAL_X_OFFSET
                                                + 1.75 * UISet.PITCH_LINE_SEP,
                             y - 1 * UISet.PITCH_LINE_SEP)
            painter.drawLine(UISet.ACCIDENTAL_X_OFFSET,
                             y + 1 * UISet.PITCH_LINE_SEP,
                             UISet.ACCIDENTAL_X_OFFSET
                                                + 1.75 * UISet.PITCH_LINE_SEP,
                             y + 0.5 * UISet.PITCH_LINE_SEP)

## END class UINote

class UINote_Whole(UINote):

    __linewidth = 3
    __pen = QtGui.QPen(QtGui.QColor(0,0,0), __linewidth,
                       Qt.SolidLine, Qt.FlatCap)
    __brush = QtGui.QBrush(Qt.NoBrush)

    def __init__(self, *args, **kwargs):
        super(UINote_Whole, self).__init__(*args, **kwargs)

    def length(self):
        return 4

    def paint(self, painter, option, widget):
        y = self._yoffset
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(-1.5*UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            y - UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            3 * UISet.PITCH_LINE_SEP - self.__linewidth,
                            2 * UISet.PITCH_LINE_SEP - self.__linewidth)
        self._paintAccidental(painter, option, widget)




class UINote_Quarter(UINote):

    __linewidth = 2
    __pen = QtGui.QPen(QtGui.QColor(0,0,0), __linewidth,
                       Qt.SolidLine, Qt.FlatCap)
    __brush = QtGui.QBrush(Qt.SolidPattern)

    def __init__(self, *args, **kwargs):
        super(UINote_Quarter, self).__init__(*args, **kwargs)

    def length(self):
        return 1

    def paint(self, painter, option, widget):
        y = self._yoffset
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(-1.25 * UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            y - UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            2.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                            2 * UISet.PITCH_LINE_SEP - self.__linewidth)
        painter.drawLine(1.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                         y,
                         1.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                         y - 7 * UISet.PITCH_LINE_SEP)
        self._paintAccidental(painter, option, widget)


class UINote_Half(UINote):

    __linewidth = 2
    __pen = QtGui.QPen(QtGui.QColor(0,0,0), __linewidth,
                       Qt.SolidLine, Qt.FlatCap)
    __brush = QtGui.QBrush(Qt.NoBrush)

    def __init__(self, *args, **kwargs):
        super(UINote_Half, self).__init__(*args, **kwargs)

    def length(self):
        return 2

    def paint(self, painter, option, widget):
        y = self._yoffset
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(-1.25 * UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            y - UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            2.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                            2 * UISet.PITCH_LINE_SEP - self.__linewidth)
        painter.drawLine(1.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                         y,
                         1.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                         y - 7 * UISet.PITCH_LINE_SEP)
        self._paintAccidental(painter, option, widget)
