import music21

from PyQt5 import QtWidgets

class UIKeySignature(QtWidgets.QGraphicsItem):

    def __init__(self, name, sharps = [], flats = [], *args, **kwargs):
        super(UIKeySignature, self).__init__(*args, **kwargs)
        self.__name = name
        self.__sharps = sharps
        self.__flats = flats

    def accidentalMarkOf(self, pitch: music21.pitch.Pitch):
        sharps = self.__sharps
        flats  = self.__flats
        if (pitch.accidental is None
                and pitch.step in sharps or pitch.step in flats):
            return music21.pitch.Accidental('natural')
        elif pitch.accidental is None:
            return None

        elif pitch.accidental.name == 'sharp' and pitch.step in sharps:
            return None
        elif pitch.accidental.name == 'sharp':
            return music21.pitch.Accidental('sharp')

        elif pitch.accidental.name == 'flat' and pitch.step in flats:
            return None
        elif pitch.accidental.name == 'flat':
            return music21.pitch.Accidental('flat')

        else:
            raise RuntimeError('Unsupported accidental \''
                               + pitch.accidental.name + '\'')

    def __str__(self):
        return 'UIKeySignature<' + self.__name + '>'

## END class UIKeySignature

def C(): return UIKeySignature('C', sharps = [])
def G(): return UIKeySignature('G', sharps = ['F'])
def D(): return UIKeySignature('D', sharps = ['F','C'])
def A(): return UIKeySignature('A', sharps = ['F','C','G'])
def E(): return UIKeySignature('E', sharps = ['F','C','G','D'])
def B(): return UIKeySignature('B', sharps = ['F','C','G','D','A'])

def F(): return UIKeySignature('F', flats = ['B'])
def Bb(): return UIKeySignature('Bb', flats = ['B','E'])
def Eb(): return UIKeySignature('Eb', flats = ['B','E','A'])
def Ab(): return UIKeySignature('Ab', flats = ['B','E','A','D'])
def Db(): return UIKeySignature('Db', flats = ['B','E','A','D','G'])
