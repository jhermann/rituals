# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, wrong-import-position
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
import sys

from .acts import Collection, task
from .util.filesys import pushd


# Build root namespace
from .acts import basic
namespace = Collection.from_module(basic, name='')  # pylint: disable=invalid-name

from .acts.testing import namespace as _
namespace.add_collection(_)

from .acts.documentation import namespace as _
namespace.add_collection(_)

from .acts.inspection import namespace as _
namespace.add_collection(_)

from .acts.releasing import namespace as _
namespace.add_collection(_)

# Activate Jekins tasks?
if os.environ.get('JENKINS_URL'):
    from .acts.jenkins import namespace as _
    namespace.add_collection(_)

# Activate devpi tasks by default?
if os.path.exists(os.path.expanduser('~/.devpi/client/current.json')):
    from .acts.devpi import namespace as _
    namespace.add_collection(_)

# Activate dpkg tasks?
if os.path.exists('debian/rules'):
    from .acts.pkgdeb import namespace as _
    namespace.add_collection(_)


def fail(message, exitcode=1):
    """Exit with error code and message."""
    sys.stderr.write('ERROR: {}\n'.format(message))
    sys.stderr.flush()
    sys.exit(exitcode)


__all__ = ['Collection', 'task', 'namespace', 'pushd', 'fail']

for _ in namespace.task_names:
    _name = _.replace('-', '_').replace('.', '_')
    __all__.append(_name)
    globals()[_name] = namespace.task_with_config(_)[0]
