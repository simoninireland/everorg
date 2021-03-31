import os
import subprocess
from xml.sax import parseString
from everorg import Exporter, HTMLParser

class PerFileExporter(Exporter):
    '''Export all notes in an Evernote export file as individual
    org mode files.'''

    def __init__(self):
        super().__init__()

    def export(self, note):
        '''Export the given note as an org mode file.'''

        # open the note file
        d = note['created']
        if self['timestamps']:
            stem = d.isoformat(timespec='seconds')
        else:
            stem = d.date().isoformat()
        fn = self.uniquifyFilename(stem, 'org')

        # trace the output if we're verbose
        if self['verbose']:
            print(fn, flush=True)

        # output all attachments
        self.exportAttachments(note)

        # convert HTML to org restructured text
        html = HTMLParser(note)
        parseString(note['content'], html)
        rst = html._buffer
        with open(fn, 'w') as f:
            print('#+title: {t}'.format(t=note['title']), file=f)
            print(file=f)
            print(rst, file=f)

        # touch file modification time if requested
        if self['maintain-timestamps']:
            if 'updated' in note:
                dt = note['updated']
            elif 'created' in note:
                dt = note['created']
            else:
                print(f'No timestamp for {fn}')
                return
            modified = dt.strftime('%Y%m%d%H%M.%S')
            rc = subprocess.call(['touch', '-m', '-t', modified, fn])
            if rc != 0:
                raise Exception(f"Can't change modification time for {fn}")
