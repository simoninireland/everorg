from xml.sax import ContentHandler
from base64 import b64decode
from dateutil.parser import parse as parse_timestamp


class EvernoteExportParser(ContentHandler):
    '''Parser an Evernote export file, emitting each note in turn.
    This is a stream parser, so it works for arbitrarily-sized exports
    by only holding one note in memory at a time.'''

    def __init__(self, exporter):
        super().__init__()
        self._exporter = exporter
        self._note = None
        self._attachments = None
        self._capture = False
        self._data = ''

    def startElement(self, tag, attrs):
        if tag == 'note':
            self._note = dict()
        elif tag == 'resource':
            self._attachment = dict()
        elif tag in ['title', 'created', 'updated', 'author', 'content', 'data', 'mime', 'file-name' ]:
            self._data = ''
            self._capture = True

    def endElement(self, tag):
        if tag == 'title':
            self._note['title'] = self._data
        elif tag == 'author':
            self._note['author'] = self._data
        elif tag == 'created':
            dt = parse_timestamp(self._data)
            self._note['created'] = dt
        elif tag == 'updated':
            dt = parse_timestamp(self._data)
            self._note['updated'] = dt
        elif tag == 'content':
            self._note['content'] = self._data.strip()
        elif tag == 'note':
            self._exporter.export(self._note)
            self._note = None
        elif tag == 'data':
            self._attachment['data'] = b64decode(self._data)
        elif tag == 'mime':
            self._attachment['mimetype'] = self._data
        elif tag == 'file-name':
            self._attachment['filename'] = self._data
        elif tag == 'resource':
            if 'attachments' not in self._note:
                self._note['attachments'] = []
            self._note['attachments'].append(self._attachment)
            self._attachments = None
        else:
            return

        self._capture = False

    def characters(self, content):
        if self._capture:
            self._data += content
