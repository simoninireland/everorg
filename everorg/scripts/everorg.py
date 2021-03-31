# Container script for importing Evernote export files into Emacs org mode
#
# Copyright (C) 2021 Simon Dobson
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/gpl.html>.

import os
from xml.sax import parse
import click
import everorg

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# TODO
# - maintain file timestamps (maintain-timestamps)
# - use dates rather than note titles (date-titles)

@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('enex')
@click.option('-f', '--files', is_flag=True, default=False, help='Each note gets its own file')
@click.option('-e', '--entries', is_flag=True, default=False, help='Each note becomes an entry in a master file')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbose output')
@click.option('-d', '--dir', default='.', help='Output directory for org mode files')
@click.option('-o', '--output', default='enex.org', help='Master org file name')
@click.option('-t', '--title', default='Evernote exports', help='Title of org master file')
@click.option('-D', '--date-titles', is_flag=True, default=False, help='Ignore note titles and use note dates')
@click.option('-T', '--timestamps', is_flag=True, default=False, help='Use full timestamps for entries and filenames')
@click.option('-M', '--maintain-times', is_flag=True, default=False, help='Maintain file timestamps as the same as notes')
def cli(enex, files, entries, verbose, dir, output, title, timestamps, maintain_times, date_titles):
    '''Convert an Evernote .enex export file to org mode.'''

    # if the output file is a path, extract the directory
    (head, tail) = os.path.split(output)
    if head != '':
        dir = head
    else:
        output = os.path.join(dir, output)

    # create the target directory if needed
    if not os.path.isdir(dir):
        os.makedirs(dir)

    # determine the exporter
    if files:
        exporter = everorg.PerFileExporter()
    elif entries:
        exporter = everorg.PerEntryExporter()
    else:
        print('No output format specified')
        exit(1)

    # fill in the styles
    exporter['dir'] = dir
    exporter['verbose'] = verbose
    exporter['orgfile'] = output
    exporter['timestamps'] = timestamps
    exporter['title'] = title
    exporter['maintain-timestamps'] = maintain_times
    exporter['date-titles'] = date_titles

    # do the export
    evernote = everorg.EvernoteExportParser(exporter)
    exporter.startExport()
    parse(enex, evernote)
    exporter.endExport()

    # newline if we've been tracing output
    if verbose:
        print()
