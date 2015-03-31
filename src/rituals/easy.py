# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
""" Default namespace for convenient wildcard import in task definition modules.
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

from invoke import Collection, ctask as task

from .util.filesys import pushd


# Build root namespace
from . import invoke_tasks as _
namespace = Collection.from_module(_, name='')  # pylint: disable=invalid-name

# Activate devpi tasks by default?
if os.path.exists(os.path.expanduser('~/.devpi/client/current.json')):
    from .acts.devpi import namespace as _
    namespace.add_collection(_)


__all__ = ['Collection', 'task', 'namespace', 'pushd']

for _ in namespace.task_names:
    __all__.append(_.replace('-', '_'))
    globals()[_.replace('-', '_')] = namespace.task_with_config(_)[0]
