# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
""" SCM helpers (currently git only).
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

from invoke import run, exceptions

from rituals.util import notify


def git_workdir_is_clean(quiet=False):
    """ Check for uncommitted changes, return `True` if everything is clean.

        Inspired by http://stackoverflow.com/questions/3878624/.
    """
    # Update the index
    run('git update-index -q --ignore-submodules --refresh')
    unchanged = True

    # Disallow unstaged changes in the working tree
    try:
        run('git diff-files --quiet --ignore-submodules --')
    except exceptions.Failure:
        unchanged = False
        if not quiet:
            notify.warning('You have unstaged changes!')
            run('git diff-files --name-status -r --ignore-submodules -- >&2')

    # Disallow uncommitted changes in the index
    try:
        run('git diff-index --cached --quiet HEAD --ignore-submodules --')
    except exceptions.Failure:
        unchanged = False
        if not quiet:
            notify.warning('Your index contains uncommitted changes!')
            run('git diff-index --cached --name-status -r --ignore-submodules HEAD -- >&2')

    return unchanged
