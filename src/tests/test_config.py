# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, missing-docstring
# pylint: disable=invalid-name, no-self-use, bad-continuation, redefined-outer-name
""" Tests for `rituals.config`.
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

#import unittest

#import pytest

from rituals import config


def test_set_maven_layout():
    config.DEFAULTS, saved = config.DEFAULTS.copy(), config.DEFAULTS
    assert saved['srcdir'] == 'src' and saved['testdir'] == 'src/tests'
    try:
        config.set_maven_layout()
        assert config.DEFAULTS['srcdir'] == 'src/main/python'
        assert config.DEFAULTS['testdir'] == 'src/test/python'
    finally:
        config.DEFAULTS = saved


def test_set_flat_layout():
    config.DEFAULTS, saved = config.DEFAULTS.copy(), config.DEFAULTS
    assert saved['srcdir'] == 'src' and saved['testdir'] == 'src/tests'
    try:
        config.set_flat_layout()
        assert config.DEFAULTS['srcdir'] == '.'
        assert config.DEFAULTS['testdir'] == 'tests'
    finally:
        config.DEFAULTS = saved
