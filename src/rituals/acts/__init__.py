# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods, invalid-name
""" rituals.acts – Task building blocks.
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

import sys

from invoke.tasks import Call


class TaskLookupError(KeyError):
    """Failed to find task definition in main `tasks` module."""


class RuntimeInvoke(Call):
    """ Invoke a task as found in the 'tasks' module namespace by name.

        This allows to override the implementations of semantic task names
        by changing their definition in `tasks.py`.
    """

    def __init__(self, task, *args, **kwargs):
        Call.__init__(self, None, *args, **kwargs)
        try:
            task + '' # check for task name
        except TypeError:
            self.task = task
            self.name = task.name
        else:
            self.name = task


    def __getattr__(self, name):
        if self.task is None:
            tasks_namespace = sys.modules['tasks']
            try:
                self.task = getattr(tasks_namespace, self.name)
            except AttributeError:
                raise TaskLookupError(self.name)
            else:
                #from rituals.util import notify
                #notify.warning("Delayed lookup of tasl '{}'".format(self.name))
                pass

        return getattr(self.task, name)


    def __str__(self):
        return "<Call {0!r}, args: {1!r} kwargs: {2!r}>".format(
            self.task.name if self.task else self.name, self.args, self.kwargs
        )


inv = RuntimeInvoke
