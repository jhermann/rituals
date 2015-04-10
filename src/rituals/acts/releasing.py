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
import sys

from invoke import Collection, ctask as task

from .. import config
from ..util import notify
from ..util.scm import provider as scm_provider
from ..util.shell import capture


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
    ctx.run('invoke clean --all build --docs dist')
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
