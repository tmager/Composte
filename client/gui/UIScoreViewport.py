from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

import client.gui.UISettings as UISet
from client.gui.UIMeasure import UIMeasure
from client.gui.UIStaffGroup import UIStaffGroup

class UIScoreViewport(QtWidgets.QGraphicsView):

    def __init__(self, measuresPerLine = 4, mode = 'ptr', width = 600,
                 zoom_min = -4, zoom_max = 4,
                 *args, **kwargs):
        super(UIScoreViewport, self).__init__(*args, **kwargs)
        self.__width = width
        self.__measuresPerLine = measuresPerLine
        self.__zoom_min = zoom_min
        self.__zoom_max = zoom_max
        self.__zoom = 0

        self.__mode = mode

        self.__selected = None

        self.__measures = []
        self.__lines = []

        self.__scoreScene = QtWidgets.QGraphicsScene(parent = self)
        self.__scoreScene.setBackgroundBrush(QtGui.QBrush(UISet.BG_COLOR))
        self.setScene(self.__scoreScene)


    def addPart(self, clef, keysig, timesig):
        measures = (len(self.__measures[0]) if self.__measures
                    else self.__measuresPerLine)
        part = []
        for i in range(measures):
            mea = UIMeasure(self.__scoreScene,
                            self.__width / self.__measuresPerLine,
                            clef, keysig, timesig,
                            parent=None)
            part.append(mea)
        self.__measures.append(part)

        if not self.__lines:
            sg = UIStaffGroup(self.__scoreScene,
                              self.__measures,
                              0, len(self.__measures[0]),
                              parent = None)
            self.__lines.append(sg)
            sg.setPos(0,0)
            self.__scoreScene.addItem(sg)

        for sg in self.__lines:
            sg.refresh()


    def addLine(self):
        for part in self.__measures:
            if part:
                lastMeasure = part[-1]
                for i in range(self.__measuresPerLine):
                    mea = UIMeasure(self.__scoreScene,
                                    self.__width / self.__measuresPerLine,
                                    lastMeasure.clef(), lastMeasure.keysig(),
                                    lastMeasure.timesig(),
                                    parent=None)
                    part.append(mea)
            else:
                raise RuntimeError("Empty measure list in UIScoreViewport.addLine")

        sg = UIStaffGroup(self.__scoreScene,
                          self.__measures,
                          len(self.__measures[0]) - self.__measuresPerLine,
                          len(self.__measures[0]),
                          parent = self.__lines[-1] if self.__lines else None)
        y = sg.parentItem().boundingRect().height()
        print(sg.parentItem().boundingRect().width())
        sg.setPos(0, y)
        self.__lines.append(sg)



    def keyPressEvent(self, ev):
        mods = QtWidgets.QApplication.keyboardModifiers()
        if mods == Qt.ControlModifier:
            # C-0 : Reset zoom
            if ev.key() == Qt.Key_0:
                self.__zoom = 0
                self.resetTransform()
            # C-- : Zoom out
            if ev.key() == Qt.Key_Minus:
                if self.__zoom != self.__zoom_min:
                    self.scale(1/1.25,1/1.25)
                    self.__zoom -= 1
            # C-= : Zoom in
            if ev.key() == Qt.Key_Equal:
                if self.__zoom != self.__zoom_max:
                    self.scale(1.25,1.25)
                    self.__zoom += 1

    def handleClick(self, partIdx, time, note):
        """
        Process a click where
        """
        pass
