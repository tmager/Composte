

from PyQt5 import QtWidgets
from client.gui.UIMeasure import UIMeasure

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
