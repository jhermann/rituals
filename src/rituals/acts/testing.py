# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, superfluous-parens, wildcard-import
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

from invoke import run, task

__all__ = ['tox']


@task(help={
    'verbose': "Make 'tox' more talkative",
    'env-list': "Override list of environments to use (e.g. 'py27,py34')",
    'opts': "Extra flags for tox",
    'pty': "Whether to run tox under a pseudo-tty",
})
def tox(verbose=False, env_list='', opts='', pty=True):
    """Perform multi-environment tests."""
    snakepits = ['/opt/pyenv/bin'] # TODO: config value
    cmd = []

    snakepits = [i for i in snakepits if os.path.isdir(i)]
    if snakepits:
        cmd += ['PATH="{}:$PATH"'.format(os.pathsep.join(snakepits),)]

    cmd += ['tox']
    if verbose:
        cmd += ['-v']
    if env_list:
        cmd += ['-e', env_list]
    cmd += opts
    cmd += ['2>&1']
    run(' '.join(cmd), echo=True, pty=pty)
