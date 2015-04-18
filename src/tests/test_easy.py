# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, missing-docstring, redefined-outer-name, invalid-name, no-self-use, bad-continuation
""" Tests for `rituals.easy`.
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
#import unittest

#import pytest

import tasks

from rituals import easy


def test_tasks_module_directory_contains_a_setup_sibling():
    """Check that imported `tasks` module is the correct one."""
    assert os.path.exists(os.path.join(os.path.dirname(tasks.__file__), "setup.py"))


def test_rituals_easy_exports_essential_names():
    for needed in ('Collection', 'task', 'namespace', 'pushd'):
        assert needed in easy.__all__, "{} missing from easy exports".format(needed)
        assert needed in dir(easy), "{} missing from easy namespace".format(needed)


def test_rituals_easy_exports_task_names():
    # Check some sample names mentioned in the docs, that's enough
    for needed in ('help', 'clean', 'test_tox', 'check_pylint', 'release_bump'):
        assert needed in easy.__all__, "{} missing from easy exports".format(needed)
        assert needed in dir(easy), "{} missing from easy namespace".format(needed)
