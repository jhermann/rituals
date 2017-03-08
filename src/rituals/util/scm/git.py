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

import os
import re
from datetime import datetime

from invoke import exceptions

from .. import notify
from .base import ProviderBase
from ..shell import capture


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
        self.run('git update-index -q --ignore-submodules --refresh', **RUN_KWARGS)
        unchanged = True

        # Disallow unstaged changes in the working tree
        try:
            self.run('git diff-files --quiet --ignore-submodules --', report_error=False, **RUN_KWARGS)
        except exceptions.Failure:
            unchanged = False
            if not quiet:
                notify.warning('You have unstaged changes!')
                self.run('git diff-files --name-status -r --ignore-submodules -- >&2', **RUN_KWARGS)

        # Disallow uncommitted changes in the index
        try:
            self.run('git diff-index --cached --quiet HEAD --ignore-submodules --', report_error=False, **RUN_KWARGS)
        except exceptions.Failure:
            unchanged = False
            if not quiet:
                notify.warning('Your index contains uncommitted changes!')
                self.run('git diff-index --cached --name-status -r --ignore-submodules HEAD -- >&2', **RUN_KWARGS)

        return unchanged


    def add_file(self, filename):
        """Stage a file for committing."""
        self.run('git add "{}"'.format(filename), **RUN_KWARGS)


    def commit(self, message):
        """Commit pending changes."""
        self.run_elective('git commit -m "{}"'.format(message))


    def tag(self, label, message=None):
        """Tag the current workdir state."""
        options = ' -m "{}" -a'.format(message) if message else ''
        self.run_elective('git tag{} "{}"'.format(options, label))


    def pep440_dev_version(self, verbose=False, non_local=False):
        """ Return a PEP-440 dev version appendix to the main version number.

            Result is ``None`` if the workdir is in a release-ready state
            (i.e. clean and properly tagged).
        """
        version = capture("python setup.py --version", echo=verbose)
        if verbose:
            notify.info("setuptools version = '{}'".format(version))

        now = '{:%Y%m%d!%H%M}'.format(datetime.now())
        tag = capture("git describe --long --tags --dirty='!{}'".format(now), echo=verbose)
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
            if non_local:
                pep440, _ = pep440.split('+', 1)

        return pep440
