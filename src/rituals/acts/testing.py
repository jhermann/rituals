# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, superfluous-parens, bad-whitespace
""" Testing tasks.
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

from invoke import run, Collection, ctask as task

from .. import config
from ..util import notify, which, add_dir2pypath


@task(default=True, help={
    'opts': "Extra flags for test runner",
})
def pytest(_, opts=''):
    """Perform standard unittests."""
    cfg = config.load()
    setup_cfg = cfg.rootjoin('setup.cfg')
    add_dir2pypath(cfg.project_root)

    try:
        console = sys.stdin.isatty()
    except AttributeError:
        console = False

    try:
        pytest_cmd = which.which("py.test").replace(cfg.project_root + os.sep, '')
    except which.WhichError:
        pytest_cmd = None

    if pytest_cmd:
        cmd = [pytest_cmd,
            '--color=yes' if console else '',
            '-c', setup_cfg,
        ]

        try:
            import pytest_cov as _
        except ImportError:
            pass
        else:
            for package in cfg.project.packages:
                if '.' not in package:
                    cmd.extend(['--cov', package,])
            for dirname in ('.', 'project.d'):
                if os.path.exists(cfg.rootjoin(dirname, 'coverage.cfg')):
                    cmd.extend(['--cov-config', cfg.rootjoin(dirname, 'coverage.cfg'),])
                    break
            cmd.extend(['--cov-report=term', '--cov-report=html', '--cov-report=xml',])

        if opts:
            cmd.append(opts)
        cmd.append(cfg.testdir)
        run(' '.join(cmd), echo=notify.ECHO)
    else:
        run('python setup.py test' + (' ' + opts if opts else ''), echo=notify.ECHO)


#_PROJECT_ROOT = config.get_project_root()
# Keep 'tox' tasks?
#if _PROJECT_ROOT and not os.path.exists(os.path.join(_PROJECT_ROOT, 'tox.ini')):
#    del tox

@task(help={
    'verbose': "Make 'tox' more talkative",
    'env-list': "Override list of environments to use (e.g. 'py27,py34')",
    'opts': "Extra flags for tox",
    'pty': "Whether to run tox under a pseudo-tty",
})
def tox(ctx, verbose=False, env_list='', opts='', pty=True):
    """Perform multi-environment tests."""
    cfg = config.load()
    add_dir2pypath(cfg.project_root)
    snakepits = ctx.test.snakepits.split(os.pathsep)
    cmd = []

    snakepits = [i for i in snakepits if os.path.isdir(i)]
    if snakepits:
        cmd += ['PATH="{}:$PATH"'.format(os.pathsep.join(snakepits),)]

    cmd += ['tox']
    if verbose:
        cmd += ['-v']
    if env_list:
        cmd += ['-e', env_list]
    cmd += opts
    cmd += ['2>&1']
    run(' '.join(cmd), echo=True, pty=pty)


namespace = Collection.from_module(sys.modules[__name__], name='test', config=dict(
    test = dict(
        snakepits = '/opt/pyenv/bin',
    ),
))
