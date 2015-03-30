# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, superfluous-parens, wildcard-import, unused-wildcard-import
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
from __future__ import absolute_import, unicode_literals, print_function

import io
import os
import re
import sys
from datetime import datetime

from invoke import run as invoke_run
from invoke import task, exceptions

from . import config
from .acts import inv
from .util import antglob, notify, which, add_dir2pypath
from .util.scm import provider as scm_provider
from .util.filesys import pushd

from .acts.basic import *
from .acts.basic import __all__ as _basic_all
from .acts.testing import *
from .acts.testing import __all__ as _testing_all


__all__ = [
    'config', 'inv', 'pushd',
    'help', 'clean', 'freeze', 'bump', 'build', 'dist', 'test', 'check',
    'release_prep',
] + _basic_all + _testing_all

_PROJECT_ROOT = config.get_project_root()


# Keep 'tox' tasks?
if not os.path.exists(os.path.join(_PROJECT_ROOT, 'tox.ini')):
    del tox
    __all__.remove('tox')

# Activate devpi tasks by default?
if os.path.exists(os.path.expanduser('~/.devpi/client/current.json')):
    from .acts.devpi import *
    from .acts.devpi import __all__ as _all
    __all__.extend(_all)
    del _all


def capture(cmd, **kw):
    """Run a command and return its stripped captured output."""
    kw = kw.copy()
    kw['hide'] = 'out'
    if not kw.get('echo', False):
        kw['echo'] = False
    try:
        return invoke_run(cmd, **kw).stdout.strip()
    except exceptions.Failure as exc:
        notify.error("Command `{}` failed with RC={}!".format(cmd, exc.result.return_code,))
        raise


def run(cmd, **kw):
    """Run a command and flush its output."""
    kw = kw.copy()
    if 'warn' not in kw:
        kw['warn'] = False  # make extra sure errors don't get silenced
    if os.name == 'posix':
        cmd += ' 2>&1'  # ensure ungarbled output
    try:
        return invoke_run(cmd, **kw)
    except exceptions.Failure as exc:
        sys.stdout.flush()
        sys.stderr.flush()
        notify.error("Command `{}` failed with RC={}!".format(cmd, exc.result.return_code,))
        raise
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


@task(default=True)
def help(): # pylint: disable=redefined-builtin
    """Invoked with no arguments."""
    run("invoke --help")
    run("invoke --list")
    notify.info("Use 'invoke -h ‹taskname›' to get detailed help.")


@task(help=dict(
    verbose="Print version information as it is collected.",
))
def bump(verbose=False):
    """Bump a development version."""
    cfg = config.load()
    version = capture("python setup.py --version", echo=verbose)
    if verbose:
        notify.info("setuptools version = '{}'".format(version))

    # TODO: Put into scm package
    now = '{:%Y%m%d!%H%M}'.format(datetime.now())
    tag = capture("git describe --long --dirty='!{}'".format(now), echo=verbose)
    if verbose:
        notify.info("git describe = '{}'".format(tag))
    try:
        tag, date, time = tag.split('!')
    except ValueError:
        date = time = ''
    tag, commits, short_hash = tag.rsplit('-', 3)
    label = tag
    if re.match(r"v[0-9]+(\.[0-9]+)*", label):
        label = label[1:]

    # Make a PEP-440 version appendix, the format is:
    # [N!]N(.N)*[{a|b|rc}N][.postN][.devN][+<local version label>]
    if commits == '0' and label == version:
        pep440 = None
    else:
        local_part = [
            re.sub(r"[^a-zA-Z0-9]+", '.', label).strip('.'),  # reduce to alphanum and dots
            short_hash,
            date + ('T' + time if time else ''),
        ]
        build_number = os.environ.get('BUILD_NUMBER', 'n/a')
        if build_number.isdigit():
            local_part.extend(['ci', build_number])
            if verbose:
                notify.info("Adding CI build ID #{} to version".format(build_number))

        local_part = [i for i in local_part if i]
        pep440 = '.dev{}+{}'.format(commits, '.'.join(local_part).strip('.'))

    # Rewrite 'setup.cfg'  TODO: refactor to helper, see also release-prep
    # with util.rewrite_file(cfg.rootjoin('setup.cfg')) as lines:
    #     ...
    setup_cfg = cfg.rootjoin('setup.cfg')
    if not pep440:
        notify.info("Working directory contains a release version '{}'".format(tag))
    elif os.path.exists(setup_cfg):
        with io.open(setup_cfg, encoding='utf-8') as handle:
            data = handle.readlines()
        changed = False
        for i, line in enumerate(data):
            if re.match(r"#? *tag_build *= *.*", line):
                verb, _ = data[i].split('=', 1)
                data[i] = '{}= {}\n'.format(verb, pep440)
                changed = True

        if changed:
            notify.info("Rewriting 'setup.cfg'...")
            with io.open(setup_cfg, 'w', encoding='utf-8') as handle:
                handle.write(''.join(data))
        else:
            notify.warning("No 'tag_build' setting found in 'setup.cfg'!")
    else:
        notify.warning("Cannot rewrite 'setup.cfg', none found!")

    if os.path.exists(setup_cfg):
        # Update metadata and print version
        egg_info = capture("python setup.py egg_info", echo=verbose)
        for line in egg_info.splitlines():
            if line.endswith('PKG-INFO'):
                pkg_info_file = line.split(None, 1)[1]
                with io.open(pkg_info_file, encoding='utf-8') as handle:
                    notify.info('\n'.join(i for i in handle.readlines() if i.startswith('Version:')).strip())
        run("python setup.py -q develop", echo=notify.ECHO or verbose)


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


@task(help={
    'opts': "Extra flags for test runner",
})
def test(opts=''):
    """Perform standard unittests."""
    cfg = config.load()
    setup_cfg = cfg.rootjoin('setup.cfg')
    add_dir2pypath(cfg.project_root)

    try:
        console = sys.stdin.isatty()
    except AttributeError:
        console = False

    try:
        pytest = which.which("py.test").replace(cfg.project_root + os.sep, '')
    except which.WhichError:
        pytest = None

    if pytest:
        cmd = [pytest,
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


@task(help=dict(
    skip_tests="Do not check test modules",
    skip_root="Do not check scripts in project root",
    reports="Create extended report?",
))
def check(skip_tests=False, skip_root=False, reports=False):
    """Perform source code checks."""
    cfg = config.load()
    add_dir2pypath(cfg.project_root)
    if not os.path.exists(cfg.testjoin('__init__.py')):
        add_dir2pypath(cfg.testjoin())

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
    for cfgfile in ('.pylintrc', 'pylint.rc', 'pylint.cfg', 'project.d/pylint.cfg'):
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


@task(name='release-prep',
    pre=[
        # Fresh build
        inv('clean', all=True),
        inv('build', docs=True),

        # Perform quality checks
        inv('test'),
        inv('check', reports=False),
    ],
    help=dict(
        commit="Commit any automatic changes and tag the release",
    ),
) # pylint: disable=too-many-branches
def release_prep(commit=True):
    """Prepare for a release."""
    cfg = config.load()
    scm = scm_provider(cfg.project_root, commit=commit)

    # Check for uncommitted changes
    if not scm.workdir_is_clean():
        notify.failure("You have uncommitted changes, please commit or stash them!")

    # TODO Check that changelog entry carries the current date

    # Rewrite 'setup.cfg'
    setup_cfg = cfg.rootjoin('setup.cfg')
    if os.path.exists(setup_cfg):
        with io.open(setup_cfg, encoding='utf-8') as handle:
            data = handle.readlines()
        changed = False
        for i, line in enumerate(data):
            if any(line.startswith(i) for i in ('tag_build', 'tag_date')):
                data[i] = '#' + data[i]
                changed = True
        if changed and commit:
            notify.info("Rewriting 'setup.cfg'...")
            with io.open(setup_cfg, 'w', encoding='utf-8') as handle:
                handle.write(''.join(data))
            scm.add_file('setup.cfg')
        elif changed:
            notify.warning("WOULD rewrite 'setup.cfg', but --no-commit was passed")
    else:
        notify.warning("Cannot rewrite 'setup.cfg', none found!")

    # Build a clean dist and check version number
    version = capture('python setup.py --version')
    run('invoke clean --all build --docs dist')
    for distfile in os.listdir('dist'):
        trailer = distfile.split('-' + version)[1]
        trailer, _ = os.path.splitext(trailer)
        if trailer and trailer[0] not in '.-':
            notify.failure("The version found in 'dist' seems to be"
                           " a pre-release one! [{}{}]".format(version, trailer))

    # Commit changes and tag the release
    scm.commit(':package: Release v{}'.format(version))
    scm.tag('v' + version, 'Release v{}'.format(version))
