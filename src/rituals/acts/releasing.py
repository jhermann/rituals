# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, superfluous-parens, bad-whitespace
""" Release tasks.
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

from invoke import Collection, ctask as task

from .. import config
from ..util import notify, shell
from ..util.scm import provider as scm_provider
from ..util.shell import capture


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


@task(
    #pre=[
    #    # Fresh build
    #    call(clean, all=True),
    #    call(build, docs=True),

        # Perform quality checks
    #    call(test),
    #    call(check, reports=False),
    #],
    help=dict(
        commit="Commit any automatic changes and tag the release",
    ),
) # pylint: disable=too-many-branches
def prep(ctx, commit=True):
    """Prepare for a release."""
    cfg = config.load()
    scm = scm_provider(cfg.project_root, commit=commit, ctx=ctx)

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

    # Update metadata and command stubs
    ctx.run('python setup.py -q develop -U')

    # Build a clean dist and check version number
    version = capture('python setup.py --version')
    ctx.run('invoke clean --all build --docs release.dist')
    for distfile in os.listdir('dist'):
        trailer = distfile.split('-' + version)[1]
        trailer, _ = os.path.splitext(trailer)
        if trailer and trailer[0] not in '.-':
            notify.failure("The version found in 'dist' seems to be"
                           " a pre-release one! [{}{}]".format(version, trailer))

    # Commit changes and tag the release
    scm.commit(ctx.release.commit.message.format(version=version))
    scm.tag(ctx.release.tag.name.format(version=version), ctx.release.tag.message.format(version=version))


namespace = Collection.from_module(sys.modules[__name__], name='release', config=dict(
    release = dict(
        commit = dict(message = ':package: Release v{version}'),
        tag = dict(name = 'v{version}', message = 'Release v{version}'),
    ),
))
