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

import os
import sys
import shlex
import shutil

from invoke import run as invoke_run
from invoke import task, exceptions

from rituals import config
from rituals.util import antglob, notify, scm, which


__all__ = [
    'config',
    'help', 'clean', 'build', 'dist', 'test', 'check',
    'release_prep',
]


def run(cmd, **kw):
    """Run a command and flush its output."""
    if os.name == 'posix':
        cmd += ' 2>&1' # ensure ungarbled output
    try:
        return invoke_run(cmd, **kw)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


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
    notify.info("Use 'invoke -h ‹taskname›' to get detailed help.")


@task(help=dict(
    docs="Also clean the documentation build area",
    backups="Also clean '*~' files etc.",
    bytecode="Also clean '.pyc', '.pyo', and package metadata",
    dist="Also clean the 'dist' dir",
    all="The same as --backups --bytecode --dist --docs",
    venv="Include an existing virtualenv (in '.' or in '.venv')",
    extra="Any extra patterns, space-separated and possibly quoted",
))
def clean(docs=False, backups=False, bytecode=False, dist=False, # pylint: disable=redefined-outer-name
        all=False, venv=False, extra=''): # pylint: disable=redefined-builtin
    """Perform house-keeping."""
    cfg = config.load()
    notify.banner("Cleaning up project files")

    patterns = ['build/', 'pip-selfcheck.json']
    if docs or all:
        patterns.append('docs/_build/')
    if dist or all:
        patterns.append('dist/')
    if backups or all:
        patterns.extend(['**/*~'])
    if bytecode or all:
        patterns.extend(['**/*.py[co]', '**/__pycache__/', 'src/*.egg-info/'])

    venv_dirs = ['bin', 'include', 'lib', 'share', 'local', '.venv']
    if venv:
        patterns.extend([i + '/' for i in venv_dirs])
    if extra:
        patterns.extend(shlex.split(extra))

    patterns = [antglob.includes(i) for i in patterns]
    if not venv:
        patterns.extend([antglob.excludes(i + '/') for i in venv_dirs])
    fileset = antglob.FileSet(cfg.project_root, patterns)
    for name in fileset:
        notify.info('rm {0}'.format(name))
        if name.endswith('/'):
            shutil.rmtree(os.path.join(cfg.project_root, name))
        else:
            os.unlink(os.path.join(cfg.project_root, name))


@task(help=dict(
    docs="Also build the documentation (with Sphinx)",
))
def build(docs=False):
    """Build the project."""
    cfg = config.load()
    run("python setup.py build", echo=notify.ECHO)

    if docs:
        for doc_path in ('docs', 'doc'):
            if os.path.exists(cfg.rootjoin(doc_path, 'conf.py')):
                break
        else:
            doc_path = None

        if doc_path:
            run("sphinx-build {0} {0}/_build".format(doc_path), echo=notify.ECHO)
        else:
            notify.warning("Cannot find either a 'docs' or 'doc' Sphinx directory!")


@task(help=dict(
    devpi="Upload the created 'dist' using 'devpi'",
    egg="Also create an EGG",
    wheel="Also create a WHL",
    auto="Create EGG for Python2, and WHL whenever possible",
))
def dist(devpi=False, egg=False, wheel=False, auto=True):
    """Distribute the project."""
    config.load()
    cmd = ["python", "setup.py", "sdist"]

    # Automatically create wheels if possible
    if auto:
        egg = sys.version_info.major == 2
        try:
            import wheel as _
            wheel = True
        except ImportError:
            wheel = False

    if egg:
        cmd.append("bdist_egg")
    if wheel:
        cmd.append("bdist_wheel")

    run("invoke clean --all build --docs test check", echo=notify.ECHO)
    run(' '.join(cmd), echo=notify.ECHO)
    if devpi:
        run("devpi upload dist/*", echo=notify.ECHO)


@task
def test():
    """Perform standard unittests."""
    cfg = config.load()
    add_root2pypath(cfg)

    try:
        console = sys.stdin.isatty()
    except AttributeError:
        console = False

    try:
        pytest = which.which("py.test").replace(cfg.project_root + os.sep, '')
    except which.WhichError:
        pytest = None

    if pytest:
        run('{}{} "{}"'.format(pytest, ' --color=yes' if console else '', cfg.testdir), echo=notify.ECHO)
    else:
        run('python setup.py test', echo=notify.ECHO)


@task(help=dict(
    skip_tests="Do not check test modules",
    skip_root="Do not check scripts in project root",
    reports="Create extended report?",
))
def check(skip_tests=False, skip_root=False, reports=False):
    """Perform source code checks."""
    cfg = config.load()
    add_root2pypath(cfg)

    cmd = 'pylint'
    for package in cfg.project.packages:
        if '.' not in package:
            cmd += ' "{}"'.format(cfg.srcjoin(package))

    if not skip_tests:
        test_py = antglob.FileSet(cfg.testdir, '**/*.py')
        test_py = [cfg.testjoin(i) for i in test_py]
        if test_py:
            cmd += ' "{0}"'.format('" "'.join(test_py))

    if not skip_root:
        root_py = antglob.FileSet('.', '*.py')
        if root_py:
            cmd += ' "{0}"'.format('" "'.join(root_py))

    cmd += ' --reports={0}'.format('y' if reports else 'n')
    for cfgfile in ('.pylintrc', 'pylint.rc', 'pylint.cfg'):
        if os.path.exists(cfgfile):
            cmd += ' --rcfile={0}'.format(cfgfile)
            break
    try:
        run(cmd, echo=notify.ECHO)
        notify.info("OK - No problems found by pylint.")
    except exceptions.Failure as exc:
        # Check bit flags within pylint return code
        if exc.result.return_code & 32:
            # Usage error (internal error in this code)
            notify.error("Usage error, bad arguments in {}?!".format(repr(cmd)))
            raise
        else:
            bits = {
                1: "fatal",
                2: "error",
                4: "warning",
                8: "refactor",
                16: "convention",
            }
            notify.warning("Some messages of type {} issued by pylint.".format(
                ", ".join([text for bit, text in bits.items() if exc.result.return_code & bit])
            ))
            if exc.result.return_code & 3:
                notify.error("Exiting due to fatal / error message.")
                raise


@task(name='release-prep', help=dict(
    commit="Commit any automatic changes and tag the release",
))
def release_prep(commit=True):
    """Prepare for a release."""
    cfg = config.load()

    # Perform quality checks
    run('inv test check', echo=notify.ECHO)

    # Check for uncommitted changes
    known_scm = True
    if os.path.exists(cfg.rootjoin('.git', 'config')):
        if not scm.git_workdir_is_clean():
            notify.failure("You have uncommitted changes, please commit or stash them!")
    else:
        known_scm = False
        notify.warning("Unsupported SCM, make sure you have committed your work!")

    # TODO Check that changelog entry carries the current date

    # Rewrite 'setup.cfg'
    setup_cfg = cfg.rootjoin('setup.cfg')
    if os.path.exists(setup_cfg):
        with open(setup_cfg) as handle:
            data = handle.readlines()
        changed = False
        for i, line in enumerate(data):
            if any(line.startswith(i) for i in ('tag_build', 'tag_date')):
                data[i] = '#' + data[i]
                changed = True
        if changed:
            notify.info("Rewriting 'setup.cfg'...")
            with open(setup_cfg, 'w') as handle:
                handle.write(''.join(data))
            run('git add setup.cfg')
    else:
        notify.warning("Cannot rewrite 'setup.cfg', none found!")

    # Build a clean dist and check version number
    version = run('python setup.py --version').stdout.strip()
    run('invoke clean --all build --docs dist')
    for distfile in os.listdir('dist'):
        trailer = distfile.split('-' + version)[1]
        trailer, _ = os.path.splitext(trailer)
        if trailer and trailer[0] not in '.-':
            notify.failure("The version found in 'dist' seems to be"
                           " a pre-release one! [{}{}]".format(version, trailer))

    # Commit changes and tag the release
    if commit:
        perform = run
    else:
        notify.warning("Due to --no-commit, these commands were skipped:")
        perform = notify.info
    perform('git commit -m ":package: Release v{}"'.format(version))
    perform('git tag "v{}"'.format(version))
