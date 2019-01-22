# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, missing-docstring
# pylint: disable=redefined-outer-name, invalid-name, no-self-use
""" Tests for `rituals.acts.testing`.
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

from invoke.context import Context
from munch import Munch as Bunch
#import pytest

import tasks  # pylint: disable=unused-import
from rituals.acts import testing


class FakeContext(Context):
    def __init__(self, taskname):
        Context.__init__(self, config=testing.namespace.configuration(taskname))
        self.memo = Bunch(cmd='')

    def run(self, command, **kwargs):
        self.memo.cmd = command

    def _modify(self, keypath, key, value):
        pass


class PytestTest(unittest.TestCase):

    def call_pytest(self, **kwargs):
        ctx = FakeContext('pytest')
        testing.pytest(ctx, **kwargs)
        return ctx.memo.cmd.split()

    def test_pytest_command_is_called(self):
        parts = self.call_pytest()
        assert parts, "testing command is not empty"
        assert parts[0].endswith('py.test'), "py.test is actually called"

    def test_pytest_task_takes_options(self):
        parts = self.call_pytest(opts='--verbose')
        assert '--verbose' in parts[-2:], "py.test option is added"

    def test_pytest_task_detects_coverage(self):
        parts = self.call_pytest(opts='--verbose')
        assert '--cov' in parts, "py.test option is added"


class ToxTest(unittest.TestCase):

    def test_tox_command_is_called(self):
        ctx = FakeContext('tox')
        testing.tox(ctx)
        parts = ctx.memo.cmd.split()
        assert parts, "tox command is not empty"
        assert 'tox' in parts[:2], "tox is actually called"

    def test_tox_task_takes_environment(self):
        ctx = FakeContext('tox')
        testing.tox(ctx, env_list='py34')
        assert '-e py34' in ctx.memo.cmd, "tox environment is selected"
