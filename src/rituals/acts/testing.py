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
import shutil
import webbrowser

from . import Collection, task
from .. import config
from ..util import notify, which, add_dir2pypath


@task(default=True, help={
    'coverage': "Open coverage report in browser tab",
    'opts': "Extra flags for test runner",
})
def pytest(ctx, coverage=False, opts=''):
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
            '-c', setup_cfg,
            '--color=yes' if console else '',
        ]

        try:
            import pytest_cov as _
        except ImportError:
            pass
        else:
            for name in cfg.project.get('packages', []) + cfg.project.get('py_modules', []):
                if '.' not in name:
                    cmd.extend(['--cov', name,])
            for dirname in ('.', 'project.d'):
                if os.path.exists(cfg.rootjoin(dirname, 'coverage.cfg')):
                    cmd.extend(['--cov-config', cfg.rootjoin(dirname, 'coverage.cfg'),])
                    break
            cmd.extend(['--cov-report=term', '--cov-report=html', '--cov-report=xml',])

        if opts:
            cmd.append(opts)
        cmd.append(cfg.testdir)
        ctx.run(' '.join(cmd))
    else:
        ctx.run('python setup.py test' + (' ' + opts if opts else ''))

    if coverage:
        # TODO: Read from "coverage.cfg [html] directory"
        cov_html = os.path.join("build/coverage_html_report", "index.html")
        if os.path.exists(cov_html):
            webbrowser.open_new_tab(cov_html)
        else:
            notify.warning('No coverage report found at "{}"!'.format(cov_html))


#_PROJECT_ROOT = config.get_project_root()
# Keep 'tox' tasks?
#if _PROJECT_ROOT and not os.path.exists(os.path.join(_PROJECT_ROOT, 'tox.ini')):
#    del tox

@task(help={
    'verbose': "Make 'tox' more talkative",
    'clean': "Remove '.tox' first",
    'env-list': "Override list of environments to use (e.g. 'py27,py34')",
    'opts': "Extra flags for tox",
})
def tox(ctx, verbose=False, clean=False, env_list='', opts=''):
    """Perform multi-environment tests."""
    cfg = config.load()
    add_dir2pypath(cfg.project_root)
    snakepits = ctx.rituals.snakepits.split(os.pathsep)
    cmd = []

    snakepits = [i for i in snakepits if os.path.isdir(i)]
    if snakepits:
        cmd += ['PATH="{}:$PATH"'.format(os.pathsep.join(snakepits),)]

    if clean and os.path.exists(cfg.rootjoin('.tox')):
        shutil.rmtree(cfg.rootjoin('.tox'))

    cmd += ['tox']
    if verbose:
        cmd += ['-v']
    if env_list:
        cmd += ['-e', env_list]
    cmd += opts
    ctx.run(' '.join(cmd))


namespace = Collection.from_module(sys.modules[__name__], name='test', config={'rituals': dict(
    #test = dict(
    #),
    snakepits = '/opt/pyenv/bin:/opt/pyrun/bin',
)})
