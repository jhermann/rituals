# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, missing-docstring
# pylint: disable=invalid-name, no-self-use, bad-continuation, redefined-outer-name
""" Tests for `rituals.util._compat`.
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
from __future__ import absolute_import, unicode_literals, print_function

import re
import datetime
#import unittest

#import pytest

from rituals.util._compat import *  # pylint: disable=redefined-builtin


def test_python_version_flags_are_consistent():
    if PYPY:
        assert not PY2
    if PY2:
        assert not PYPY


def test_isodate_is_formatted_as_expected():
    result = isodate()
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", result)


def test_isodate_with_microseconds_is_formatted_as_expected():
    result = isodate(microseconds=True)
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}", result)


def test_isodate_with_specific_date_works():
    result = isodate(datetime.datetime(1998, 1, 23, 12, 34, 56))
    assert result == "1998-01-23 12:34:56"
