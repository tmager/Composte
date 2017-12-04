from PyQt5 import QtWidgets, QtCore
from client.gui.UIStaff import UIStaff
import client.gui.UISettings as UISet

class UIStaffGroup(QtWidgets.QGraphicsItemGroup):

    def __init__(self, canvas, measureLists, startMeasure, endMeasure,
                 *args, **kwargs):
        super(UIStaffGroup, self).__init__(*args, **kwargs)
        self.__canvas = canvas
        self.__measureLists = measureLists
        self.__startMeasure = startMeasure
        self.__endMeasure = endMeasure
        self.__staves = []
        self.refresh()

    def length(self):
        """
        Return the time length of this staff group, i.e. the time between the
        first beat of this line and the first beat of the next one.
        """
        if not self.__staves:
            return 0
        return self.__staves[0].length()

    def refresh(self):
        self.__updateStaves()
        self.__updatePositions()

    def __updateStaves(self):
        for s in self.__staves:
            self.__canvas.removeItem(s)
        self.__staves = [UIStaff(ml, self.__startMeasure, self.__endMeasure,
                                 parent = self)
                         for ml in self.__measureLists]


    def __updatePositions(self):
        y_offset = 0
        for s in self.__staves:
            y = s.boundingRect().y()
            h = s.boundingRect().height()
            s.setPos(0, y_offset)
            y_offset += y + h


    def boundingRect(self):
        childBoundRect = self.childrenBoundingRect()
        x = childBoundRect.x()
        y = childBoundRect.y()
        width = childBoundRect.width()
        height = childBoundRect.height()
        return QtCore.QRectF(x,
                             y - UISet.STAFF_GROUP_Y_PAD,
                             width,
                             height + 2 * UISet.STAFF_GROUP_Y_PAD)
