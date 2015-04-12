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

from invoke import ctask as task, exceptions

from . import config
from .util import antglob, notify, shell, add_dir2pypath
from .util.scm import provider as scm_provider

from .acts.basic import *


@task(default=True)
def help(_dummy_ctx): # pylint: disable=redefined-builtin
    """Invoked with no arguments."""
    shell.run("invoke --help")
    shell.run("invoke --list")
    notify.info("Use 'invoke -h ‹taskname›' to get detailed help.")


@task(help=dict(
    verbose="Print version information as it is collected.",
    pypi="Do not create a local part for the PEP-440 version.",
))
def bump(ctx, verbose=False, pypi=False):
    """Bump a development version."""
    cfg = config.load()
    scm = scm_provider(cfg.project_root, commit=False, ctx=ctx)

    # Check for uncommitted changes
    if not scm.workdir_is_clean():
        notify.warning("You have uncommitted changes, will create a time-stamped version!")

    pep440 = scm.pep440_dev_version(verbose=verbose, non_local=pypi)

    # Rewrite 'setup.cfg'  TODO: refactor to helper, see also release-prep
    # with util.rewrite_file(cfg.rootjoin('setup.cfg')) as lines:
    #     ...
    setup_cfg = cfg.rootjoin('setup.cfg')
    if not pep440:
        notify.info("Working directory contains a release version!")
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
        egg_info = shell.capture("python setup.py egg_info", echo=True if verbose else None)
        for line in egg_info.splitlines():
            if line.endswith('PKG-INFO'):
                pkg_info_file = line.split(None, 1)[1]
                with io.open(pkg_info_file, encoding='utf-8') as handle:
                    notify.info('\n'.join(i for i in handle.readlines() if i.startswith('Version:')).strip())
        ctx.run("python setup.py -q develop", echo=True if verbose else None)


@task(help=dict(
    docs="Also build the documentation (with Sphinx)",
))
def build(ctx, docs=False):
    """Build the project."""
    cfg = config.load()
    ctx.run("python setup.py build")

    if docs:
        for doc_path in ('docs', 'doc'):
            if os.path.exists(cfg.rootjoin(doc_path, 'conf.py')):
                break
        else:
            doc_path = None

        if doc_path:
            ctx.run("sphinx-build {0} {0}/_build".format(doc_path))
        else:
            notify.warning("Cannot find either a 'docs' or 'doc' Sphinx directory!")


@task(help=dict(
    devpi="Upload the created 'dist' using 'devpi'",
    egg="Also create an EGG",
    wheel="Also create a WHL",
    auto="Create EGG for Python2, and WHL whenever possible",
))
def dist(ctx, devpi=False, egg=False, wheel=False, auto=True):
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

    ctx.run("invoke clean --all build --docs test check")
    ctx.run(' '.join(cmd))
    if devpi:
        ctx.run("devpi upload dist/*")


@task(help=dict(
    skip_tests="Do not check test modules",
    skip_root="Do not check scripts in project root",
    reports="Create extended report?",
))
def check(ctx, skip_tests=False, skip_root=False, reports=False):
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
        shell.run(cmd, report_error=False, runner=ctx.run)
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
