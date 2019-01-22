# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, unused-wildcard-import, missing-docstring
# pylint: disable=redefined-outer-name, invalid-name, no-self-use
""" Tests for `rituals.acts.inspection`.
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

#import pytest
from munch import Munch as Bunch
from invoke.context import Context

import tasks  # pylint: disable=unused-import
from rituals.acts import inspection


class FakeContext(Context):
    def __init__(self, taskname):
        Context.__init__(self, config=inspection.namespace.configuration(taskname))
        self.memo = Bunch(cmd='')

    def run(self, command, **kwargs):
        self.memo.cmd = command

    def _modify(self, keypath, key, value):
        pass


class PylintTest(unittest.TestCase):

    def call_pylint(self, **kwargs):
        ctx = FakeContext('pylint')
        inspection.pylint(ctx, **kwargs)
        return ctx.memo.cmd.split()

    def test_pylint_command_is_called(self):
        parts = self.call_pylint()
        assert parts, "checking command is not empty"
        assert parts[0] == 'pylint', "pylint is actually called"
        assert '--reports=n' in parts, "no pylint reports by default"
        assert '--rcfile=project.d/pylint.cfg' in parts, "pylint config is loaded"
        assert '"src/tests/conftest.py"' in parts, "test files in pylint command: " + repr(parts)
        assert '"setup.py"' in parts, "root files in pylint command: " + repr(parts)

    def test_pylint_can_skip_test_files(self):
        parts = self.call_pylint(skip_tests=True)
        assert not any(i.endswith('/src/tests/conftest.py"') for i in parts), "no test files in pylint command: " + repr(parts)

    def test_pylint_can_skip_root_files(self):
        parts = self.call_pylint(skip_root=True)
        assert '"setup.py"' not in parts, "no root files in pylint command: " + repr(parts)

    def test_pylint_report_can_be_activated(self):
        parts = self.call_pylint(reports=True)
        assert '--reports=y' in parts, "no pylint reports by default"
