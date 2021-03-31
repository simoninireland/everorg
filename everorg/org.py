import re
from xml.sax import ContentHandler

# formatting corrections
whitelines = re.compile(r'^\s*\n$', re.MULTILINE)
blanklines = re.compile(r'^\n{2,}', re.MULTILINE)
emptyemphasis = re.compile(r'([*/])\s*\1', re.MULTILINE)
listelement = re.compile(r'^\s*(([o-]\s+)|([0-9]+\.\s+))')

# Unicode characters that don't render correctly in Emacs
special = {0xA0: ' ',        # nbsp
           0x2026: '...',    # elipsis
           0x2014: '--',     # long hyphen
           }

# A weird bug that changes some , and ' to "undefined"
weirdundefined = re.compile(r'\wundefined')


class HTMLParser(ContentHandler):
    '''A simple HTML to org mode parser.'''

    def __init__(self, note, titles=0):
        super().__init__()
        self._note = note
        self._buffer = ''
        self._titles = titles
        self._depth = []
        self._mentions = 0
        self._linking = False

    def startElement(self, tag, attrs):
        if tag == 'ol':
            self._depth.append(1)
        elif tag == 'ul':
            self._depth.append(-1)
        elif tag == 'li':
            if self._depth[-1] < 0:
                self._buffer += ' ' * (3 * (len(self._depth) - 1)) + "- "
            else:
                self._buffer += ' ' * (3 * (len(self._depth) - 1)) + str(self._depth[-1]) + ". "
                self._depth[-1] += 1
        elif tag == 'i' or tag == 'em':
            self._buffer += '/'
        elif tag == 'b' or tag == 'strong':
            self._buffer += '*'
        elif tag == 'h1' or tag == 'h2' or tag == 'h3':
            d = int(tag[1])
            self._buffer += '*' * (d + self._titles) + ' '
        elif tag == 'a':
            href = attrs['href']
            if not href.startswith('evernote:'):    # ignore evernote-local links
                self._buffer += '[[' + href + ']['
                self._linking = True
        elif tag == 'en-media':
            a = self._note['attachments'][self._mentions]
            mimetype = a['mimetype']
            if mimetype.startswith('image/'):
                self._buffer += '[[file:' + a['filename'] + ']]'
            else:
                self._buffer += '[[file:' + a['filename'] + '][An image]]'
            self._mentions += 1

    def endElement(self, tag):
        if tag == 'div':
            self._buffer += '\n'
        elif tag == 'br':
            self._buffer += '\n'
        elif tag == 'hr':
            self._buffer += '\n-----\n'
        elif tag == 'ol' or tag == 'ul':
            self._depth = self._depth[:-1]
        elif tag == 'i' or tag == 'em':
            self._buffer += '/'
        elif tag == 'b' or tag == 'strong':
            self._buffer += '*'
        elif tag == 'a':
            if self._linking:
                self._buffer += ']]'
                self._linking = False
        else:
            #print(f'ignored /{tag}')
            pass

    def characters(self, content):
        self._buffer += content

    def wrap(self, s, width=80):
        '''Wrap long lines in a string.'''
        newtext = ''
        while len(s) > 0:
            # get the next line
            split = s.find('\n')
            if split < 0:
                line = s
                s = ''
            else:
                line = s[:split]
                s = s[split + 1:]
                if split == 0:
                    newtext += '\n'

            # if we're a list element, count the indentation
            m = listelement.match(line)
            if m is None:
                indent = 0
            else:
                indent = len(m[0])

            # wrap the line
            while len(line) > width:
                remaining = width - indent

                # look for opening of a link
                split = 1
                while split >= 0:
                    split = line.find('[[', 0, remaining)
                    if split >= 0:
                        # protect all of link as a single line
                        midlink = line.find('][', split)
                        endlink = line.find(']]', split)
                        newtext += line[:split]
                        if midlink < 0:
                            # an embedding, probably of an image, appears as the link target
                            textlen = endlink - split
                        else:
                            # a link with descriptive text, appears as text
                            textlen = endlink - midlink
                        if remaining - textlen <= 0:
                            newtext += '\n' + (' ' * indent)
                            remaining = width - indent
                        newtext += line[split:endlink + 2]
                        line = line[endlink + 2:]
                        remaining -= textlen
                if remaining <= 0:
                    newtext += '\n' + (' ' * indent)
                    remaining = width - indent

                # split non-link parts
                split = max([line.rfind(sep, 0, remaining) for sep in [' ', ',', '.', ':', ';', '!', '?']])
                if split >= 0:
                    if line[split] == ' ':
                        # drop trailing spaces
                        newtext += line[:split]
                    else:
                        newtext += line[:split + 1]
                    newtext += '\n' + (' ' * indent)
                    line = line[split + 1:].lstrip()
            if len(line) > 0:
                newtext += line + '\n'
        return newtext

    def endDocument(self):
        '''Clean all leading and trailing whitespace, and any duplicated blank lines,
        and wrap long lines.'''
        self._buffer = self._buffer.translate(special)
        self._buffer = blanklines.sub('\n', whitelines.sub('\n', self._buffer))
        self._buffer = emptyemphasis.sub('', self._buffer)
        self._buffer = weirdundefined.sub('', self._buffer)
        self._buffer = self.wrap(self._buffer.strip())
