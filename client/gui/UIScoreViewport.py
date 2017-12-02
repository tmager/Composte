from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

from client.gui import UISettings

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
        self.__scoreScene.setBackgroundBrush(QtGui.QBrush(UISettings.BG_COLOR))
        self.setScene(self.__scoreScene)



    def addLine(self):
        if self.__measures:
            lastMeasure = self.__measures[-1]
            for i in range(self.__measuresPerLine):
                mea = UIMeasure(self.__scoreScene,
                                self.__width / self.__measuresPerLine,
                                lastMeasure.clef(), lastMeasure.keysig(),
                                lastMeasure.timesig(),
                                parent=None)
                self.__measures.append(mea)

            sg = UIStaffGroup(self.__measures,
                              len(self.__measures) - self.__measuresPerLine,
                              len(self.__measures),
                              self.__width,
                              parent = None)
            self.__scoreScene.addItem(sg)


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
