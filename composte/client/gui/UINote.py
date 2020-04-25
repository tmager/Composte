"""
Graphics types for all of the various types of notes.

In retrospect, the class structure in this is *awful*, but reimplementing it has
not been a priority.
"""


import music21

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt

from util.classExceptions import virtualmethod
import client.gui.UISettings as UISet


def ntypeFromMusic21(note: music21.note.Note):
    """
    Given a music21Note, return the class of a UINote which would have the
    appropriate duration.  Raise a runtime error if the note is not of a length
    that is supported.
    """
    ntypeMap = {
        ('whole',   0) : UINote_Whole,
        ('half',    0) : UINote_Half,
        ('half',    1) : UINote_Half_Dotted,
        ('quarter', 0) : UINote_Quarter,
        ('quarter', 1) : UINote_Quarter_Dotted,
        ('eighth', 0)  : UINote_Eighth,
        ('eighth', 1)  : UINote_Eighth_Dotted,
        ('16th', 0)  : UINote_16th,
        ('16th', 1)  : UINote_16th_Dotted,
    }
    if (note.duration.type, note.duration.dots) in ntypeMap:
        return ntypeMap[(note.duration.type, note.duration.dots)]
    else:
        raise RuntimeError('Unsupported note duration ' + str(note.duration))


class UINote(QtWidgets.QGraphicsItem):

    """
    A superclass for all graphics notes.
    """

    __accidentalLineWidth = 1.5
    __accidentalPen = QtGui.QPen(QtGui.QColor(0,0,0),
                                 __accidentalLineWidth,
                                 Qt.SolidLine, Qt.FlatCap)
    __accidentalBrush = QtGui.QBrush(Qt.NoBrush)
    __dotPen = QtGui.QPen(Qt.NoPen)
    __dotBrush = QtGui.QBrush(QtGui.QColor(0,0,0), Qt.SolidPattern)

    # Overridden by subclasses
    _length = None


    def __init__(self, pitch, clef, keysig, *args, **kwargs):
        super(UINote, self).__init__(*args, **kwargs)
        self.__pitch = pitch
        self.__clef = clef
        self.__keysig = keysig

        self._yoffset = (8 * UISet.PITCH_LINE_SEP
                          - self.__clef.position(pitch) * UISet.PITCH_LINE_SEP)

    @classmethod
    def length(cls):
        """
        Return the length of the note, in quarter note increments.
        """
        return cls._length

    def boundingRect(self):
        """
        Return a rectangle enclosing the entire drawn object.
        """
        y = self._yoffset
        return QtCore.QRectF(-3.5 * UISet.PITCH_LINE_SEP - 5,
                             y - 7 * UISet.PITCH_LINE_SEP,
                             7 * UISet.PITCH_LINE_SEP + 10,
                             9 * UISet.PITCH_LINE_SEP + 10)


    def _paintAccidental(self, painter, option, widget):
        """
        Draw in accidental marks, if appropriate.
        """
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

    def _paintDot(self, painter, option, widget):
        """
        Paint a dot on the current note.
        """
        y = self._yoffset
        painter.setBrush(self.__dotBrush)
        painter.setPen(self.__dotPen)
        painter.drawEllipse(UISet.DOT_X_OFFSET - UISet.DOT_RADIUS,
                            y + UISet.DOT_Y_OFFSET - UISet.DOT_RADIUS,
                            2 * UISet.DOT_RADIUS,
                            2 * UISet.DOT_RADIUS)
## END class UINote

class UINote_Whole(UINote):

    _length = 4.0

    __linewidth = 3
    __pen = QtGui.QPen(QtGui.QColor(0,0,0), __linewidth,
                       Qt.SolidLine, Qt.FlatCap)
    __brush = QtGui.QBrush(Qt.NoBrush)

    def __init__(self, *args, **kwargs):
        super(UINote_Whole, self).__init__(*args, **kwargs)

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


class UINote_Half(UINote):

    _length = 2.0

    __linewidth = 2
    __pen = QtGui.QPen(QtGui.QColor(0,0,0), __linewidth,
                       Qt.SolidLine, Qt.FlatCap)
    __brush = QtGui.QBrush(Qt.NoBrush)

    def __init__(self, *args, **kwargs):
        super(UINote_Half, self).__init__(*args, **kwargs)

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

class UINote_Half_Dotted(UINote_Half):

    _length = 3.0

    def __init__(self, *args, **kwargs):
        super(UINote_Half_Dotted, self).__init__(*args, **kwargs)

    def paint(self, painter, option, widget):
        super(UINote_Half_Dotted, self).paint(painter, option, widget)
        self._paintDot(painter, option, widget)


class UINote_Quarter(UINote):

    _length = 1.0

    __linewidth = 2
    __pen = QtGui.QPen(QtGui.QColor(0,0,0), __linewidth,
                       Qt.SolidLine, Qt.FlatCap)
    __brush = QtGui.QBrush(Qt.SolidPattern)

    def __init__(self, *args, **kwargs):
        super(UINote_Quarter, self).__init__(*args, **kwargs)

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


class UINote_Quarter_Dotted(UINote_Quarter):

    _length = 1.5

    def __init__(self, *args, **kwargs):
        super(UINote_Quarter_Dotted, self).__init__(*args, **kwargs)

    def paint(self, painter, option, widget):
        super(UINote_Quarter_Dotted, self).paint(painter, option, widget)
        self._paintDot(painter, option, widget)


class UINote_Eighth(UINote):

    _length = 0.5

    __linewidth = 2
    __pen = QtGui.QPen(QtGui.QColor(0,0,0), __linewidth,
                       Qt.SolidLine, Qt.FlatCap)
    __brush = QtGui.QBrush(Qt.SolidPattern)
    __stemBrush = QtGui.QBrush(Qt.NoBrush)

    def __init__(self, *args, **kwargs):
        super(UINote_Eighth, self).__init__(*args, **kwargs)

    def paint(self, painter, option, widget):
        y = self._yoffset
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(-1.25 * UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            y - UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            2.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                            2 * UISet.PITCH_LINE_SEP - self.__linewidth)
        path = QtGui.QPainterPath()
        path.moveTo(1.5 * UISet.PITCH_LINE_SEP - self.__linewidth, y)
        path.lineTo(1.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                    y - 7 * UISet.PITCH_LINE_SEP)
        path.lineTo(3 * UISet.PITCH_LINE_SEP - self.__linewidth,
                    y - 5.5 * UISet.PITCH_LINE_SEP)
        painter.setBrush(self.__stemBrush)
        painter.drawPath(path)
        self._paintAccidental(painter, option, widget)

class UINote_Eighth_Dotted(UINote_Eighth):

    _length = 0.75

    def __init__(self, *args, **kwargs):
        super(UINote_Eighth_Dotted, self).__init__(*args, **kwargs)

    def paint(self, painter, option, widget):
        super(UINote_Eighth_Dotted, self).paint(painter, option, widget)
        self._paintDot(painter, option, widget)


class UINote_16th(UINote):

    _length = 0.25

    __linewidth = 2
    __pen = QtGui.QPen(QtGui.QColor(0,0,0), __linewidth,
                       Qt.SolidLine, Qt.FlatCap)
    __brush = QtGui.QBrush(Qt.SolidPattern)
    __stemBrush = QtGui.QBrush(Qt.NoBrush)

    def __init__(self, *args, **kwargs):
        super(UINote_16th, self).__init__(*args, **kwargs)

    def paint(self, painter, option, widget):
        y = self._yoffset
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(-1.25 * UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            y - UISet.PITCH_LINE_SEP + self.__linewidth/2,
                            2.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                            2 * UISet.PITCH_LINE_SEP - self.__linewidth)
        path = QtGui.QPainterPath()
        path.moveTo(1.5 * UISet.PITCH_LINE_SEP - self.__linewidth, y)
        path.lineTo(1.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                    y - 7 * UISet.PITCH_LINE_SEP)
        path.lineTo(3 * UISet.PITCH_LINE_SEP - self.__linewidth,
                    y - 5.5 * UISet.PITCH_LINE_SEP)
        painter.setBrush(self.__stemBrush)
        painter.drawPath(path)
        painter.drawLine(1.5 * UISet.PITCH_LINE_SEP - self.__linewidth,
                         y - 6 * UISet.PITCH_LINE_SEP,
                         3 * UISet.PITCH_LINE_SEP - self.__linewidth,
                         y - 4.5 * UISet.PITCH_LINE_SEP)
        self._paintAccidental(painter, option, widget)


class UINote_16th_Dotted(UINote_16th):

    _length = 0.375

    def __init__(self, *args, **kwargs):
        super(UINote_16th_Dotted, self).__init__(*args, **kwargs)

    def paint(self, painter, option, widget):
        super(UINote_16th_Dotted, self).paint(painter, option, widget)
        self._paintDot(painter, option, widget)
