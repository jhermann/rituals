# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, missing-docstring, redefined-outer-name, invalid-name, no-self-use
""" Tests for `rituals.acts`.
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

import pytest

import tasks
from rituals.invoke_tasks import clean
from rituals.acts import *


def test_task_lookup_error_is_indeed_a_lookup_error():
    with pytest.raises(LookupError):
        raise TaskLookupError("tilt!")


class RuntimeInvokeTests(unittest.TestCase):

    def test_looking_up_clean_task_in_tasks_by_name(self):
        task = RuntimeInvoke('clean')
        assert task.name == 'clean'
        assert task.task == None

    def test_initializing_with_a_task_object(self):
        task = RuntimeInvoke(clean)
        assert task.name == 'clean'
        assert task.task == clean
