import music21

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from client.gui import UINote, UIClef, UITimeSignature, UIKeySignature
from client.gui.UIScoreViewport import UIScoreViewport

class Editor(QtWidgets.QMainWindow):

    __noteTypeLookup = {
            'whole'   : UINote.UINote_Whole,
            'half'    : UINote.UINote_Half,
            'quarter' : UINote.UINote_Quarter
        }
    __defaultClef = UIClef.treble()
    __defaultTimeSignature = UITimeSignature.UITimeSignature(4,4)
    __defaultKeySignature = UIKeySignature.C()

    def __init__(self, client, *args, **kwargs):
        super(Editor, self).__init__(*args, **kwargs)
        self.__client = client
        self.__makeUI()
        self.__resetAll()

    def update(self, startOffset, endOffset):
        self.__ui_scoreViewport.update(self.__client.project(),
                                       startOffset, endOffset)

    def __resetAll(self):
        try:
            self.__ui_scoreViewport.update(self.__client.project(), None, None)
        except RuntimeError as e:
            self.__debugConsoleWrite(e.msg)

    def __makeUI(self):
        self.__ui_mainSplitter = QtWidgets.QSplitter(Qt.Vertical, self)

        self.__ui_scoreViewport = \
                            UIScoreViewport(parent = self.__ui_mainSplitter)

        # For some reason this string can't be blank, but it can be anything
        # else that isn't a font.
        self.__ui_debugConsole_font = QtGui.QFont('nothing')
        self.__ui_debugConsole_font.setStyleHint(QtGui.QFont.Monospace)

        self.__ui_debugConsole_layoutWidget = \
                            QtWidgets.QWidget(self.__ui_mainSplitter)
        self.__ui_debugConsole_layout = \
                    QtWidgets.QVBoxLayout(self.__ui_debugConsole_layoutWidget)
        self.__ui_debugConsole_layoutWidget \
                            .setLayout(self.__ui_debugConsole_layout)
        self.__ui_debugConsole_log = \
                            QtWidgets.QTextEdit(self.__ui_debugConsole_layoutWidget)
        self.__ui_debugConsole_log.setReadOnly(True)
        self.__ui_debugConsole_log.setFont(self.__ui_debugConsole_font)
        self.__ui_debugConsole_input = \
                            QtWidgets.QLineEdit(self.__ui_debugConsole_layoutWidget)
        self.__ui_debugConsole_input.setFont(self.__ui_debugConsole_font)
        self.__ui_debugConsole_input.returnPressed \
                            .connect(self.__processDebugInput)
        self.__ui_debugConsole_layout.addWidget(self.__ui_debugConsole_log)
        self.__ui_debugConsole_layout.addWidget(self.__ui_debugConsole_input)
        self.__ui_debugConsole_layoutWidget.hide()

        self.__ui_mainSplitter.addWidget(self.__ui_scoreViewport)
        self.__ui_mainSplitter.addWidget(self.__ui_debugConsole_layoutWidget)

        # Make the debug console not take up most of the window.
        self.__ui_mainSplitter.setStretchFactor(0, 3)

        self.setCentralWidget(self.__ui_mainSplitter)

        self.__makeMenuBar()
        self.__makeToolbar()

    def __makeMenuBar(self):
        self.__ui_filemenu = QtWidgets.QMenu('File', parent = self)
        self.__ui_editmenu = QtWidgets.QMenu('Edit', parent = self)

        self.__ui_act_debugConsole = \
                        self.__ui_filemenu.addAction('Debug Console Enabled')
        self.__ui_act_debugConsole.setCheckable(True)
        self.__ui_act_debugConsole \
                        .setShortcut(QtGui.QKeySequence(Qt.Key_Escape))
        self.__ui_act_debugConsole.changed.connect(self.__toggleDebug)

        self.__ui_act_quit = self.__ui_filemenu.addAction('Quit')
        self.__ui_act_quit.setShortcut(QtGui.QKeySequence('Ctrl+Q'))
        self.__ui_act_quit.triggered.connect(self.close)

        self.__ui_act_edit = self.__ui_editmenu.addAction('Play')
        self.__ui_act_edit.setShortcut(QtGui.QKeySequence('Ctrl+space'))
        self.__ui_act_edit.triggered.connect(self.__handlePlay)

        self.__ui_menubar = QtWidgets.QMenuBar(parent = self)
        self.__ui_menubar.addMenu(self.__ui_filemenu)
        self.__ui_menubar.addMenu(self.__ui_editmenu)

        self.setMenuBar(self.__ui_menubar)


    def __makeToolbar(self):
        pass

    def printChatMessage(self, msg):
        self.__debugConsoleWrite(msg)

    def __debugConsoleWrite(self, msg):
        self.__ui_debugConsole_log.append(msg)

    def __toggleDebug(self):
        self.__ui_debugConsole_layoutWidget \
                            .setVisible(self.__ui_act_debugConsole.isChecked())
        if self.__ui_act_debugConsole.isChecked():
            self.__ui_debugConsole_input.setFocus()

    def __debugConsoleHelp(self, fn = None):
        if fn is None:
            msg = 'help/?       --  Display this help message'
            self.__debugConsoleWrite(msg)
        if fn == 'clear' or fn is None:
            msg = 'clear        --  Clear the debug console history'
            self.__debugConsoleWrite(msg)
        if fn == 'insert' or fn is None:
            msg = ('insert/i PART_INDEX PITCH NOTE_TYPE OFFSET\n'
                   '    Insert a NOTE_TYPE into the indicated part, at \n'
                   '    quarter-note-offset OFFSET and with the given PITCH')
            self.__debugConsoleWrite(msg)


    def __handleAddPart(self, clef):
        if self.__ui_scoreViewport.parts() == 0:
            self.__ui_scoreViewport.addPart(clef, self.__defaultKeySignature,
                                            self.__defaultTimeSignature)
        else:
            self.__ui_scoreViewport.addPart(clef)

    def __handlePlay(self, part = 0):
        ## TODO: Implement me!
        raise NotImplementedError

    def __handleAddLine(self):
        self.__ui_scoreViewport.addLine()

    def __handleInsertNote(self, part, pitch, ntype, offset):
        ## TODO: This actually needs to do server interaction; this is just for
        ## testing.
        try:
            self.__ui_scoreViewport.insertNote(part, pitch, ntype, offset)
        except ValueError as e:
            self.__debugConsoleWrite(str(e))

    def __handleDeleteNote(self, part, pitch, offset):
        ## TODO: This actually needs to do server interaction; this is just for
        ## testing.
        if not self.__ui_scoreViewport.deleteNote(part, pitch, offset):
            self.__debugConsoleWrite('No note ' + str((part, pitch, offset)))

    def __handleChatMessage(self, msg):
        ## TODO: This actually needs to do server interaction; this is just for
        ## testing.
        self.printChatMessage(msg)

    def __processDebugInput(self):
        text = self.__ui_debugConsole_input.text()
        self.__ui_debugConsole_input.clear()
        if not text:
            return
        cmdstrs = map(str.strip, text.split(';'))
        for cmdstr in cmdstrs:
            self.__processDebugCommand(cmdstr)

    def __processDebugCommand(self, cmdstr):
        args = cmdstr.split(' ')
        cmd = args[0].lower()
        args.pop(0)

        if cmd in ['clear']:
            self.__ui_debugConsole_log.clear()
        elif cmd in ['chat', 'c']:
            self.__handleChatMessage(' '.join(args))
        elif cmd in ['play', 'p']:
            if len(args) == 0:
                self.__handlePlay()
            if len(args) == 1:
                try:
                    part = int(args[0])
                except ValueError:
                    msg = 'Unable to generate part index from \'' + args[1] + '\''
                    self.__debugConsoleWrite(msg)
                    return
                self.__handlePlay(part)
            else:
                self.__debugConsoleHelp('play')
        elif cmd in ['addpart']:
            self.__handleAddPart(self.__defaultClef)
        elif cmd in ['addline']:
            self.__handleAddLine()
        elif cmd in ['insert','i']:
            if len(args) != 4:
                self.__debugConsoleHelp('insert')
                return

            try:
                part = int(args[0])
            except ValueError:
                msg = 'Unable to generate part index from \'' + args[1] + '\''
                self.__debugConsoleWrite(msg)

            try:
                pitch = music21.pitch.Pitch(args[1])
            except music21.pitch.PitchException:
                msg = 'Unable to generate pitch from \'' + args[1] + '\''
                self.__debugConsoleWrite(msg)
                return

            if args[2].lower() in Editor.__noteTypeLookup:
                ntype = Editor.__noteTypeLookup[args[2].lower()]
            else:
                msg = 'Unknown note type \'' + args[2] + '\''
                self.__debugConsoleWrite(msg)
                return

            try:
                offset = float(args[3])
            except ValueError:
                msg = 'Unable to generate time offset from \'' + args[3] + '\''
                self.__debugConsoleWrite(msg)
                return

            self.__handleInsertNote(part, pitch, ntype, offset)
        elif cmd in ['delete','d']:
            if len(args) != 3:
                self.__debugConsoleHelp('delete')
                return

            try:
                part = int(args[0])
            except ValueError:
                msg = 'Unable to generate part index from \'' + args[1] + '\''
                self.__debugConsoleWrite(msg)
                return

            try:
                pitch = music21.pitch.Pitch(args[1])
            except music21.pitch.PitchException:
                msg = 'Unable to generate pitch from \'' + args[1] + '\''
                self.__debugConsoleWrite(msg)
                return

            try:
                offset = float(args[2])
            except ValueError:
                msg = 'Unable to generate time offset from \'' + args[2] + '\''
                self.__debugConsoleWrite(msg)
                return

            self.__handleDeleteNote(part, pitch, offset)
        else:
            self.__debugConsoleHelp()
