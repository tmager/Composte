from client.gui.UIStaff import UIStaff

class UIStaffGroup(QtWidgets.QGraphicsItemGroup):

    def __init__(self, measureLists, startMeasure, endMeasure,
                 *args, **kwargs):
        super(UIStaffGroup, self).__init__(*args, **kwargs)
        self.__measureLists = measureLists
        self.__startMeasure = startMeasure
        self.__endMeasure = endMeasure
        self.__staves = [UIStaff(ml, startMeasure, endMeasure,
                                 parent = self)
                         for ml in measureLists]

    def length(self):
        """
        Return the time length of this staff group, i.e. the time between the
        first beat of this line and the first beat of the next one.
        """
        if not self.__staves:
            return 0
        return self.__staves[0].length()
