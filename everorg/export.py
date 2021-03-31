import os
from re import compile, sub
from xml.sax import parseString
from datetime import datetime
from mimetypes import guess_extension
from everorg import HTMLParser

unprintable = compile('[^a-zA-Z0-9_\.-]+')

class Exporter:
    '''Base class for exporters, with helper methods.'''

    def __init__(self):
        super().__init__()
        self._styles = dict()

    def __getitem__(self, k):
        return self._styles[k]

    def __setitem__(self, k, v):
        self._styles[k] = v

    def contains(self, k):
        return k in self._styles

    def keys(self):
        return self._styles.keys()

    def uniquifyFilename(self, ofn, ext):
        '''Return a unique version of the given filename, avoiding name
        clashes and dodgy characters.

        '''

        # convert dodgy characters in stem
        stem = sub(unprintable, '_', ofn, count=0)

        # build full filename
        dir = self['dir']
        i = 0
        fn = f'{stem}.{ext}'
        path = os.path.join(dir, fn)

        # ensure filename is unique
        while os.path.isfile(path):
            # append a sequence number if needed for uniqueness
            i += 1
            fn = f'{stem}-{i}.{ext}'
            path = os.path.join(dir, fn)
        return path

    def dateToFilename(self, d, ext):
        '''Convert a date and an extension to a unique filename.'''
        fn = '{y}-{m}-{d}'.format(y=d.year, m=d.month, d=d.day)
        return self.uniquifyFilename(fn, ext)

    def titleToFilename(self, t, ext):
        '''Convert a string, assumed to be a note title, to a unique
        filename.'''
        return self.uniquifyFilename(t, ext)

    def exportAttachments(self, note):
        '''Export all the attachments, re-writing the filenames appropriately.'''
        if 'attachments' in note:
            for a in note['attachments']:
                basename = os.path.basename(a['filename'])
                if basename == '':
                    # empty filename, synthesise one
                    ext = guess_extension(a['mimetype'])
                    ext = ext[1:]
                    path = self.uniquifyFilename('attachment', ext)
                else:
                    (stem, ext) = os.path.splitext(basename)
                    if ext is not None:
                        ext = ext[1:]
                    path = self.uniquifyFilename(stem, ext)

                # trace the attachment if we're verbose
                if self['verbose']:
                    print(f'Attachment {path}')

                # update the attachment filename to the generated file
                a['filename'] = os.path.join('.', os.path.basename(path))

                # write out the data
                with open(path, 'wb') as f:
                    f.write(a['data'])

    def startExport(self):
        pass

    def endExport(self):
        pass
