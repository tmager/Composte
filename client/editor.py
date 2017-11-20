from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from client.gui.UIScoreViewport import UIScoreViewport

class Editor(QtWidgets.QMainWindow):

    sig_viewportClick = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Editor, self).__init__(*args, **kwargs)
        self.__makeUI()

    def __makeUI(self):
        self.__ui_scoreViewport = UIScoreViewport(parent = self)
        self.setCentralWidget(self.__ui_scoreViewport)

        self.__makeMenuBar()
        self.__makeToolbar()

    def __makeMenuBar(self):
        self.__ui_filemenu = QtWidgets.QMenu("File", parent = self)
        self.__ui_act_quit = self.__ui_filemenu.addAction("Quit")

        self.__ui_act_quit.triggered.connect(self.close)

        self.__ui_menubar = QtWidgets.QMenuBar(parent = self)
        self.__ui_menubar.addMenu(self.__ui_filemenu)

        self.setMenuBar(self.__ui_menubar)


    def __makeToolbar(self):
        pass
