from client.gui.UIStaff import UIStaff

class UIStaffGroup(QtWidgets.QGraphicsItemGroup):

    def __init__(self, streams, measures, *args, **kwargs):
        super(UIStaffGroup, self).__init__(args, kwargs)
        self.__measures = measures
        self.__staves = []

    def getMusicLength(self):
        """
        Return the time length of this staff group, i.e. the time between the
        first beat of this line and the first beat of the next one.
        """
        # TODO: Make this work
        return 4 * self.__measures

    def createStaff(self, idx):
        while len(self.__staves) <= idx:
            st = UIStaff()
            if self.__staves:
                st.setParentItem(self.__staves[-1])
            self.__staves.append(st)
            self.addToGroup(self.__staves[-1])
