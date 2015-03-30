# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, missing-docstring, redefined-outer-name, invalid-name, no-self-use, bad-continuation
""" Tests for `rituals.util.filesys`.
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

import os
import tempfile
#import unittest

import pytest

from rituals.util.filesys import pushd


@pytest.fixture(scope='module')
def tmpdir():
    return tempfile.gettempdir()


def test_pushd_changes_cwd_to_passed_parameter(tmpdir):
    with pushd(tmpdir):
        assert os.getcwd() == tmpdir


def test_pushd_puts_old_cwd_into_context_var(tmpdir):
    cwd = os.getcwd()
    with pushd(tmpdir) as saved:
        assert saved == cwd


def test_pushd_restores_old_cwd(tmpdir):
    cwd = os.getcwd()
    with pushd(tmpdir):
        assert os.getcwd() != cwd
    assert os.getcwd() == cwd
