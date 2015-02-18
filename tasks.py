# -*- coding: utf-8 -*-
# pylint: disable=superfluous-parens,wildcard-import,unused-wildcard-import,bad-continuation
""" Project automation for Invoke.
"""

import os
import shlex

from invoke import run, task

from setup import *
from rituals.util.antglob import *


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
    cmd = 'pylint "{0}"'.format(srcfile('src', project['name']))
    if not skip_tests:
        test_root = srcfile('src', 'tests')
        test_py = FileSet(test_root, [includes('**/*.py')])
        test_py = [os.path.join(test_root, i) for i in test_py]
        if test_py:
            cmd += ' "{0}"'.format('" "'.join(test_py))
    run(cmd)

@task
def ci(): # pylint: disable=invalid-name
    """Perform continuous integration tasks."""
    run("invoke clean --all build --docs test check")
