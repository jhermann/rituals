# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, missing-docstring, redefined-outer-name, invalid-name, no-self-use, bad-continuation
""" Tests for `rituals.util`.
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
import unittest

#import pytest

from rituals import util


class SearchFileUpwardsTest(unittest.TestCase):

    def test_searching_for_a_missing_file_terminates(self):
        assert util.search_file_upwards('only_crazies_would_name_a_file_like_this') is None

    def test_we_can_find_our_own_setup_and_tasks_modules(self):
        home = os.path.dirname(__file__)
        root = util.search_file_upwards('setup.py', base=home)
        assert os.path.exists(os.path.join(root, 'tasks.py'))

    def test_file_is_found_when_located_in_the_base_dir(self):
        home = os.path.dirname(__file__)
        root = util.search_file_upwards('conftest.py', base=home)
        assert root == home

    def test_search_starts_in_cwd_by_default(self):
        home = os.path.dirname(__file__)
        cwd = os.getcwd()
        try:
            os.chdir(home)
            root = util.search_file_upwards('conftest.py')
            assert root == home
        finally:
            os.chdir(cwd)
