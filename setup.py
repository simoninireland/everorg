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

from setuptools import setup

setup(
    name='everorg',
    version=0.1,
    py_modules=[ 'everorg' ],
    install_requires=[
        "python-dateutil", "click", 
    ],
    entry_points='''
        [console_scripts]
        everorg=everorg.scripts.everorg:cli
    ''',
)
