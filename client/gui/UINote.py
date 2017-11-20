from PyQt5 import QtWidgets, QtGui

from util.classExceptions import virtualmethod
import gui.UISettings

class UINote(QtWidgets.QGraphicsItem):

    def __init__(self):
        super(Note, self).__init__(*args, **kwargs)
        self.selected = False

    @virtualmethod
    def length(self):
        """Return the length of the note, in quarter note increments."""
