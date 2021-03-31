import os
from xml.sax import parseString
from everorg import Exporter, HTMLParser

class PerEntryExporter(Exporter):
    '''Export all notes as entries in a single org mode file.'''

    def __init__(self):
        super().__init__()
        self._f = None

    def startExport(self):
        self._f = open(self['orgfile'], "w")
        print('#+title: {t}'.format(t=self['title']), file=self._f)
        print('#+startup: overview', file=self._f)
        print('', file=self._f)

    def endExport(self):
        self._f.close()
        self._f = None

    def export(self, note):
        '''Export the given note as an entry in the master org mode file.'''

        # trace the output if we're verbose
        if self['verbose']:
            print('.', end='', flush=True)

        # output all attachments
        self.exportAttachments(note)

        # convert HTML to org restructured text
        html = HTMLParser(note, titles=1)
        parseString(note['content'], html)
        rst = html._buffer
        print('* ' + note['title'], file=self._f)
        print('', file=self._f)
        print(rst, file=self._f)
        print('', file=self._f)
