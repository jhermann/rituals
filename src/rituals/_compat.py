# -*- coding: utf-8 -*-
# pylint: disable=
""" PY2/3 compatibility helpers.
"""
# Copyright ⓒ  2015 Jürgen Hermann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# The full LICENSE file and source are available at
#    https://github.com/jhermann/rituals

import sys
import datetime

PY2 = sys.version_info[0] == 2
PYPY = hasattr(sys, 'pypy_translation_info')


def isodate(datestamp=None, microseconds=False):
    """Return current or given time formatted according to ISO-8601."""
    datestamp = datestamp or datetime.datetime.now()
    if not microseconds:
        datestamp = datestamp - datetime.timedelta(microseconds=datestamp.microsecond)
    return datestamp.isoformat(b' ' if PY2 else u' ')
