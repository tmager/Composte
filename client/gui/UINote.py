from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt

from util.classExceptions import virtualmethod
import client.gui.UISettings as UISettings

class UINote(QtWidgets.QGraphicsItem):

    def __init__(self, accidentalMark = None, *args, **kwargs):
        super(UINote, self).__init__(*args, **kwargs)
        self.selected = False
        self.__accidentalMark = accidentalMark

    @virtualmethod
    def length(self):
        """
        Return the length of the note, in quarter note increments.
        """

    @virtualmethod
    def boundingRect(self):
        """
        Return a rectangle enclosing the entire object.
        """

    def accidentalMark(self):
        return self.__accidentalMark

    def setAccidentalMark(self, mark):
        self.__accidentalMark = mark

    def __paintAccidental(self):
        pass


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
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(-1.5*UISettings.PITCH_LINE_SEP + self.__linewidth/2,
                            -UISettings.PITCH_LINE_SEP + self.__linewidth/2,
                            3 * UISettings.PITCH_LINE_SEP - self.__linewidth,
                            2 * UISettings.PITCH_LINE_SEP - self.__linewidth)
        self.__paintAccidental()

    def boundingRect(self):
        return QtCore.QRectF(-1.5*UISettings.PITCH_LINE_SEP - self.__linewidth/2,
                             -UISettings.PITCH_LINE_SEP - self.__linewidth/2,
                             3 * UISettings.PITCH_LINE_SEP + self.__linewidth,
                             2 * UISettings.PITCH_LINE_SEP + self.__linewidth)




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
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(-1.25 * UISettings.PITCH_LINE_SEP + self.__linewidth/2,
                            -UISettings.PITCH_LINE_SEP + self.__linewidth/2,
                            2.5 * UISettings.PITCH_LINE_SEP - self.__linewidth,
                            2 * UISettings.PITCH_LINE_SEP - self.__linewidth)
        painter.drawLine(1.5 * UISettings.PITCH_LINE_SEP - self.__linewidth,
                         0,
                         1.5 * UISettings.PITCH_LINE_SEP - self.__linewidth,
                         -7 * UISettings.PITCH_LINE_SEP)
        self.__paintAccidental()

    def boundingRect(self):
        return QtCore.QRectF(-1.25 * UISettings.PITCH_LINE_SEP - self.__linewidth/2,
                             -7 * UISettings.PITCH_LINE_SEP,
                             2.5 * UISettings.PITCH_LINE_SEP + self.__linewidth,
                             9 * UISettings.PITCH_LINE_SEP + self.__linewidth)



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
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(-1.25 * UISettings.PITCH_LINE_SEP + self.__linewidth/2,
                            -UISettings.PITCH_LINE_SEP + self.__linewidth/2,
                            2.5 * UISettings.PITCH_LINE_SEP - self.__linewidth,
                            2 * UISettings.PITCH_LINE_SEP - self.__linewidth)
        painter.drawLine(1.5 * UISettings.PITCH_LINE_SEP - self.__linewidth,
                         0,
                         1.5 * UISettings.PITCH_LINE_SEP - self.__linewidth,
                         -7 * UISettings.PITCH_LINE_SEP)
        self.__paintAccidental()

    def boundingRect(self):
        return QtCore.QRectF(-1.25 * UISettings.PITCH_LINE_SEP - self.__linewidth/2,
                             -7 * UISettings.PITCH_LINE_SEP,
                             2.5 * UISettings.PITCH_LINE_SEP + self.__linewidth,
                             9 * UISettings.PITCH_LINE_SEP + self.__linewidth)
