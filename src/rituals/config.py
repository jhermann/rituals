# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, bad-whitespace
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

    # this assumes an importable setup.py
    # TODO: maybe call "python setup.py egg_info" for metadata
    if cfg.project_root not in sys.path:
        sys.path.append(cfg.project_root)
    try:
        from setup import project # pylint: disable=no-name-in-module
    except ImportError:
        from setup import setup_args as project # pylint: disable=no-name-in-module
    cfg.project = Bunch(project)

    return cfg


def set_maven_layout():
    """Switch default project layout to Maven-like."""
    DEFAULTS.update(
        srcdir = 'src/main/python',
        testdir = 'src/test/python',
    )


def set_flat_layout():
    """Switch default project layout to everything top-level."""
    DEFAULTS.update(
        srcdir = '.',
        testdir = 'tests',
    )
