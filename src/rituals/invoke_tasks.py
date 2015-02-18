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

from invoke import run, task

from rituals.util.antglob import *

# this assumes an importable setup.py
# TODO: maybe call "python setup.py egg_info" for metadata
_ROOT = os.path.dirname(sys.modules['tasks'].__file__)
if _ROOT not in sys.path:
    sys.path.append(_ROOT)
from setup import *

__all__ = ['help', 'clean', 'build', 'test', 'check']


def add_root2path():
    """Add project root to PYTHONPATH, e.g. for pylint."""
    py_path = os.environ.get('PYTHONPATH', '')
    if project_root not in py_path.split(os.pathsep):
        py_path = ''.join([project_root, os.pathsep if py_path else '', py_path])
        os.environ['PYTHONPATH'] = py_path


@task(default=True)
def help(): # pylint: disable=redefined-builtin
    """Invoked with no arguments."""
    run("invoke --help")
    run("invoke --list")
    print("Use 'invoke -h ‹taskname›' to get detailed help.")


@task
def clean(docs=False, backups=False, bytecode=False, dist=False,
        all=False, venv=False, extra=''): # pylint: disable=redefined-builtin
    """Perform house-cleaning."""
    patterns = ['build', 'pip-selfcheck.json']
    if docs or all:
        patterns.append('docs/_build')
    if dist or all:
        patterns.append('dist')
    if backups or all:
        patterns.extend(['*~', '**/*~'])
    if bytecode or all:
        patterns.extend(['*.py[co]', '**/*.py[co]', '**/__pycache__'])

    venv_dirs = ['bin', 'include', 'lib', 'share', 'local']
    if venv:
        patterns.extend(venv_dirs)
    if extra:
        patterns.extend(shlex.split(extra))

    patterns = [includes(i) for i in patterns]
    if not venv:
        patterns.extend([excludes(i + '/**/*') for i in venv_dirs])
    fileset = FileSet(project_root, patterns)
    for name in fileset:
        print('rm {0}'.format(name))
        os.unlink(os.path.join(project_root, name))


@task
def build(docs=False):
    """Build the project."""
    os.chdir(project_root)
    run("python setup.py build")
    if docs and os.path.exists(srcfile("docs", "conf.py")):
        run("sphinx-build docs docs/_build")


@task
def test():
    """Perform standard unittests."""
    os.chdir(project_root)
    run('python setup.py test')


@task
def check(skip_tests=False):
    """Perform source code checks."""
    os.chdir(project_root)
    add_root2path()

    cmd = 'pylint "{0}"'.format(srcfile('src', project['name']))
    if not skip_tests:
        test_root = srcfile('src', 'tests')
        test_py = FileSet(test_root, [includes('**/*.py')])
        test_py = [os.path.join(test_root, i) for i in test_py]
        if test_py:
            cmd += ' "{0}"'.format('" "'.join(test_py))
    run(cmd)
