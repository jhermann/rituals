# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, missing-docstring
# pylint: disable=redefined-outer-name, invalid-name, no-self-use
""" Tests for `rituals.util.notify`.
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
#import unittest

import pytest

from rituals.util.notify import *


SAID = "I've got this terrible pain in all the diodes down my left hand side!"


def no_ansi(text):
    """Kill any ANSI escape sequences."""
    return re.sub(r"\x1b.+?m", "", text)


def test_output_a_banner_to_stderr(capsys):
    banner(SAID)
    silence, text = capsys.readouterr()
    assert repr(no_ansi(text.replace(SAID, '~'))) == repr('~\n')
    assert silence == ''


def test_output_an_info_message_to_stdout(capsys):
    info(SAID)
    text, silence = capsys.readouterr()
    assert repr(text.replace(SAID, '~')) == repr('~\n')
    assert silence == ''


def test_output_a_warning_to_stderr(capsys):
    warning(SAID)
    silence, text = capsys.readouterr()
    assert repr(no_ansi(text.replace(SAID, '~'))) == repr('WARNING: ~\n')
    assert silence == ''


def test_output_an_error_to_stderr(capsys):
    error(SAID)
    silence, text = capsys.readouterr()
    assert repr(no_ansi(text.replace(SAID, '~'))) == repr('ERROR: ~\n')
    assert silence == ''


def test_output_a_failure_message_to_stderr_and_exit(capsys):
    with pytest.raises(SystemExit):
        failure(SAID)
    silence, text = capsys.readouterr()
    assert repr(no_ansi(text.replace(SAID, '~'))) == repr('ERROR: ~\n')
    assert silence == ''
