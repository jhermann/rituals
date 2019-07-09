# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, too-few-public-methods
""" Provider base class.
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

from .. import notify
from ..shell import run


class ProviderBase():
    """Base class for SCM providers."""


    def __init__(self, workdir, commit=True, **kwargs):  # pylint: disable=unused-argument
        self.ctx = kwargs.pop('ctx', None)
        self.workdir = workdir
        self._commit = commit


    def run(self, cmd, *args, **kwargs):
        """Run a command."""
        runner = self.ctx.run if self.ctx else None
        return run(cmd, runner=runner, *args, **kwargs)


    def run_elective(self, cmd, *args, **kwargs):
        """Run a command, or just echo it, depending on `commit`."""
        if self._commit:
            return self.run(cmd, *args, **kwargs)
        else:
            notify.warning("WOULD RUN: {}".format(cmd))
            kwargs = kwargs.copy()
            kwargs['echo'] = False
            return self.run('true', *args, **kwargs)
