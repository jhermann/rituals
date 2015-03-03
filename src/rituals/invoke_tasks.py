# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, superfluous-parens, wildcard-import
""" Common tasks for invoke.
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

# TODO: Move task bodies to common_tasks module, and just keep Invoke wrappers here

import os
import sys
import shlex
import shutil

from invoke import run, task

from rituals import config
from rituals.util import antglob


__all__ = ['config', 'help', 'clean', 'build', 'dist', 'test', 'check']


def add_root2pypath(cfg):
    """Add project root to PYTHONPATH, e.g. for pylint."""
    py_path = os.environ.get('PYTHONPATH', '')
    if cfg.project_root not in py_path.split(os.pathsep):
        py_path = ''.join([cfg.project_root, os.pathsep if py_path else '', py_path])
        os.environ['PYTHONPATH'] = py_path


@task(default=True)
def help(): # pylint: disable=redefined-builtin
    """Invoked with no arguments."""
    run("invoke --help")
    run("invoke --list")
    print("Use 'invoke -h ‹taskname›' to get detailed help.")


@task
def clean(docs=False, backups=False, bytecode=False, dist=False, # pylint: disable=redefined-outer-name
        all=False, venv=False, extra=''): # pylint: disable=redefined-builtin
    """Perform house-cleaning."""
    cfg = config.load()

    patterns = ['build/', 'pip-selfcheck.json']
    if docs or all:
        patterns.append('docs/_build/')
    if dist or all:
        patterns.append('dist/')
    if backups or all:
        patterns.extend(['**/*~'])
    if bytecode or all:
        patterns.extend(['**/*.py[co]', '**/__pycache__/', 'src/*.egg-info/'])

    venv_dirs = ['bin', 'include', 'lib', 'share', 'local']
    if venv:
        patterns.extend([i + '/' for i in venv_dirs])
    if extra:
        patterns.extend(shlex.split(extra))

    patterns = [antglob.includes(i) for i in patterns]
    if not venv:
        patterns.extend([antglob.excludes(i + '/') for i in venv_dirs])
    fileset = antglob.FileSet(cfg.project_root, patterns)
    for name in fileset:
        print('rm {0}'.format(name))
        if name.endswith('/'):
            shutil.rmtree(os.path.join(cfg.project_root, name))
        else:
            os.unlink(os.path.join(cfg.project_root, name))


@task
def build(docs=False):
    """Build the project."""
    cfg = config.load()
    run("python setup.py build")
    if docs and os.path.exists(cfg.rootjoin("docs", "conf.py")):
        run("sphinx-build docs docs/_build")


@task
def dist(devpi=False, egg=True, wheel=False):
    """Distribute the project."""
    config.load()
    cmd = ["python", "setup.py", "sdist"]
    if egg:
        cmd.append("bdist_egg")
    if wheel:
        cmd.append("bdist_wheel")

    run("invoke clean --all build --docs test") # TODO: check
    run(' '.join(cmd))
    if devpi:
        run("devpi upload dist/*")


@task
def test():
    """Perform standard unittests."""
    cfg = config.load()
    add_root2pypath(cfg)

    try:
        console = sys.stdin.isatty()
    except AttributeError:
        console = False

    if console and os.path.exists('bin/py.test'):
        run('bin/py.test --color=yes {0}'.format(cfg.testdir))
    else:
        run('python setup.py test')


@task
def check(skip_tests=False):
    """Perform source code checks."""
    cfg = config.load()
    add_root2pypath(cfg)

    cmd = 'pylint "{0}"'.format(cfg.srcjoin(cfg.project.name))
    if not skip_tests:
        test_py = antglob.FileSet(cfg.testdir, '**/*.py')
        test_py = [cfg.testjoin(i) for i in test_py]
        if test_py:
            cmd += ' "{0}"'.format('" "'.join(test_py))
    run(cmd) # TODO: check return code and only abort on errors (or set threshold via options)
