

from PyQt5 import QtWidgets, QtCore
from client.gui.UIMeasure import UIMeasure
import client.gui.UISettings as UISet

class UIStaff(QtWidgets.QGraphicsItemGroup):

    def __init__(self, measureList, startMeasure, endMeasure, *args, **kwargs):
        super(UIStaff, self).__init__(*args, **kwargs)
        self.__measureList = measureList
        self.__startMeasure = startMeasure
        self.__endMeasure = endMeasure

        xpos = 0
        for i in range(startMeasure, endMeasure):
            self.__measureList[i].setParentItem(self)
            self.__measureList[i].setPos(xpos, 0)
            xpos += self.__measureList[i].width()

    def measures(self):
        """
        Return the number of measures that this UIStaff is displaying.
        """
        return self.__endMeasure - self.__startMeasure

    def length(self):
        return sum(map(length(self.__measures[self.__startMeasure
                                              :self.__endMeasure])))

    def boundingRect(self):
        childBoundRect = self.childrenBoundingRect()
        x = childBoundRect.x()
        y = childBoundRect.y()
        width = childBoundRect.width()
        height = childBoundRect.height()
        return QtCore.QRectF(x - UISet.STAFF_X_PAD,
                             y - UISet.STAFF_Y_PAD,
                             width + 2 * UISet.STAFF_X_PAD,
                             height + 2 * UISet.STAFF_Y_PAD)
