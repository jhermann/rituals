# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, missing-docstring, redefined-outer-name, invalid-name, no-self-use, bad-continuation
""" Tests for `rituals.invoke_tasks`.
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

import os
#import unittest

#import pytest
from invoke.tasks import Task

import tasks
from rituals import invoke_tasks


def test_task_py_path_has_setup_py():
    """Check that imported `tasks` module is the correct one."""
    assert os.path.exists(os.path.join(os.path.dirname(tasks.__file__), "setup.py"))


def test_all_tasks_are_exported():
    """Check that all defined tasks are also exported."""
    defined_tasks = set(k
        for k, v in vars(invoke_tasks).items()
        if isinstance(v, Task))
    assert defined_tasks <= set(invoke_tasks.__all__)


def test_config_is_exported():
    """Check that `config` is exported."""
    assert 'config' in invoke_tasks.__all__
