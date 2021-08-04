# -*- coding: utf-8 -*-
# pylint: disable=
""" Project configuration and layout.
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
from pathlib import Path

from munch import Munch as Bunch


DEFAULTS = dict(
    srcdir = 'src',
    testdir = 'src/tests',
    project_root = None,
    project = {},
    cwd = None,
    rootjoin = None,
    srcjoin = None,
    testjoin = None,
)


def get_project_root():
    """ Determine location of `tasks.py`."""
    try:
        tasks_py = sys.modules['tasks']
    except KeyError:
        return None
    else:
        return os.path.abspath(os.path.dirname(tasks_py.__file__))


def load():
    """ Load and return configuration as a ``Bunch``.

        Values are based on ``DEFAULTS``, and metadata from ``setup.py``.
    """
    from .util import buildsys

    cfg = Bunch(DEFAULTS)
    # TODO: override with contents of [rituals] section in setup.cfg

    cfg.project_root = get_project_root()
    if not cfg.project_root:
        raise RuntimeError("No tasks module is imported, cannot determine project root")

    cfg.rootjoin = lambda *names: os.path.join(cfg.project_root, *names)
    cfg.srcjoin = lambda *names: cfg.rootjoin(cfg.srcdir, *names)
    cfg.testjoin = lambda *names: cfg.rootjoin(cfg.testdir, *names)
    cfg.cwd = os.getcwd()
    os.chdir(cfg.project_root)
    cfg.project = buildsys.project_meta()

    return cfg


def is_maven_layout(project_dir):
    """Apply heuristics to check if the given path is a Maven project."""
    project_dir = Path(project_dir)
    result = ((project_dir / 'src/main/tests').exists()
        and (project_dir / 'src/main/python').exists()
    )
    return result


def set_maven_layout():
    """Switch default project layout to Maven-like."""
    DEFAULTS.update(
        srcdir = 'src/main/python',
        testdir = 'src/test/python',
    )


def is_flat_layout(project_dir):
    """Apply heuristics to check if the given path is a 'flat' project."""
    # Right now, we only take care of projects where repo name and package name are equivalent
    project_dir = Path(project_dir)
    result = ((project_dir / 'tests').exists()
        and (project_dir / project_dir.name.replace('-', '_') / '__init__.py').exists()
    )
    return result


def set_flat_layout():
    """Switch default project layout to everything top-level."""
    DEFAULTS.update(
        srcdir = '.',
        testdir = 'tests',
    )
