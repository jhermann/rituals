# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, superfluous-parens, wildcard-import
""" Basic tasks.
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
import shlex
import shutil

from invoke import run, task

from .. import config
from ..util import antglob, notify
from ..util._compat import isodate


__all__ = ['clean', 'freeze']


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

    # Add patterns based on given parameters
    venv_dirs = ['bin', 'include', 'lib', 'share', 'local', '.venv']
    patterns = ['build/', 'pip-selfcheck.json']
    if docs or all:
        patterns.append('docs/_build/')
    if dist or all:
        patterns.append('dist/')
    if backups or all:
        patterns.extend(['**/*~'])
    if bytecode or all:
        patterns.extend([
            '**/*.py[co]', '**/__pycache__/', '*.egg-info/',
            cfg.srcjoin('*.egg-info/')[len(cfg.project_root)+1:],
        ])
    if venv:
        patterns.extend([i + '/' for i in venv_dirs])
    if extra:
        patterns.extend(shlex.split(extra))

    # Build fileset
    patterns = [antglob.includes(i) for i in patterns]
    if not venv:
        # Do not scan venv dirs when not cleaning them
        patterns.extend([antglob.excludes(i + '/') for i in venv_dirs])
    fileset = antglob.FileSet(cfg.project_root, patterns)

    # Iterate over matches and remove them
    for name in fileset:
        notify.info('rm {0}'.format(name))
        if name.endswith('/'):
            shutil.rmtree(os.path.join(cfg.project_root, name))
        else:
            os.unlink(os.path.join(cfg.project_root, name))


@task(help=dict(
    local="If in a virtualenv that has global access, do not output globally installed packages",
))
def freeze(local=False):
    """Freeze currently instaleld requirements."""
    cmd = 'pip freeze{}'.format(' --local' if local else '')
    frozen = run(cmd, hide='out').stdout
    with io.open('frozen-requirements.txt', 'w', encoding='ascii') as out:
        out.write("# Requirements frozen by 'pip freeze' on {}\n".format(isodate()))
        out.write(frozen)
    notify.info("Frozen {} requirements.".format(len(frozen.splitlines()),))
