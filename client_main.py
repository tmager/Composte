#!/usr/bin/env python3

import sys
from client.editor import Editor

from PyQt5 import QtWidgets

def main(argv):
    app = QtWidgets.QApplication(sys.argv)
    ed = Editor()
    ed.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
