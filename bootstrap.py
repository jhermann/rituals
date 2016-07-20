#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Python Project 0dependency Bootstrap Wizard.

    Right now, just a set of notes for a later implementation.

    Requirements:

        * Support at least Python 2.7 and 3.4.
        * One simple command to set up a working development environment.
        * Report any problems of the underlying tools in a way humans can understand.
        * Abstract away environment specifics (auto-detect typical scenarios).
        * Work "offline", i.e. without a direct connection to the Internet.
          [detect devpi? load a pre-build dependency bundle from an env var location?
           work with available pre-installed packages? …]
        * Self-upgrade from well-known location on demand (python bootstrap.py upgrade).

    Sources of inspiration / re-use:
        * https://pypi.python.org/pypi/pyutilib.virtualenv/
        * https://virtualenv.pypa.io/en/latest/reference.html?highlight=bootstrap#creating-your-own-bootstrap-scripts
        * https://github.com/socialplanning/fassembler/blob/master/fassembler/create-venv-script.py
        * https://github.com/pypa/virtualenv/issues/632


    Ubuntu Trusty castrates pyvenv (omits ensurepip), thus:

        /usr/bin/pyvenv-3.4 --without-pip py34
        cd py34
        curl -skS https://bootstrap.pypa.io/get-pip.py | bin/python -


    Copyright ⓒ  2015 Jürgen Hermann

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 2 as
    published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    The full LICENSE file and source are available at
        https://github.com/jhermann/rituals
"""
# TODO: Actually implement this
