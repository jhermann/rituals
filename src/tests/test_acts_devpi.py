# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, missing-docstring
# pylint: disable=redefined-outer-name, invalid-name, no-self-use
""" Tests for `rituals.acts.devpi`.
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

import unittest

from munch import Munch as Bunch
import pytest

import tasks  # pylint: disable=unused-import
from rituals.acts import devpi


class GetDevpiUrlTest(unittest.TestCase):

    def test_get_devpi_url_delivers_simpleindex_url(self):
        ctx = Bunch(run=lambda cmd, **_: Bunch(stdout="first: line\n   simpleindex: THE-URL/\n other: foobar\n"))
        url = devpi.get_devpi_url(ctx)
        assert url == "THE-URL", "get_devpi_url() extracted the URL"


    def test_get_devpi_url_ignores_ansi_codes(self):
        ctx = Bunch(run=lambda cmd, **_: Bunch(stdout="first: line\n\x1b1m   simpleindex: THE-URL/\x1b0m\n other: foobar\n"))
        url = devpi.get_devpi_url(ctx)
        assert url == "THE-URL", "get_devpi_url() extracted the URL"


    def test_get_devpi_url_detects_missing_simpleindex_url(self):
        ctx = Bunch(run=lambda cmd, **_: Bunch(stdout="   notsosimpleindex: THE-URL/"))
        with pytest.raises(LookupError):
            _ = devpi.get_devpi_url(ctx)
