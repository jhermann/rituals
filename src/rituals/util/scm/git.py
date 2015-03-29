# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, no-self-use
""" git SCM provider.
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

from invoke import run, exceptions

from .. import notify
from .base import ProviderBase


RUN_KWARGS = dict()


class GitProvider(ProviderBase):
    """ git SCM provider.

        Expects a working `git` executable in the path,
        having a reasonably current version.
    """
    key = 'git'


    def workdir_is_clean(self, quiet=False):
        """ Check for uncommitted changes, return `True` if everything is clean.

            Inspired by http://stackoverflow.com/questions/3878624/.
        """
        # Update the index
        run('git update-index -q --ignore-submodules --refresh', **RUN_KWARGS)
        unchanged = True

        # Disallow unstaged changes in the working tree
        try:
            run('git diff-files --quiet --ignore-submodules --', **RUN_KWARGS)
        except exceptions.Failure:
            unchanged = False
            if not quiet:
                notify.warning('You have unstaged changes!')
                run('git diff-files --name-status -r --ignore-submodules -- >&2', **RUN_KWARGS)

        # Disallow uncommitted changes in the index
        try:
            run('git diff-index --cached --quiet HEAD --ignore-submodules --', **RUN_KWARGS)
        except exceptions.Failure:
            unchanged = False
            if not quiet:
                notify.warning('Your index contains uncommitted changes!')
                run('git diff-index --cached --name-status -r --ignore-submodules HEAD -- >&2', **RUN_KWARGS)

        return unchanged


    def add_file(self, filename):
        """Stage a file for committing."""
        run('git add "{}"'.format(filename), **RUN_KWARGS)


    def commit(self, message):
        """Commit pending changes."""
        self.run_elective('git commit -m "{}"'.format(message))


    def tag(self, label):
        """Tag the current workdir state."""
        self.run_elective('git tag "{}"'.format(label))
