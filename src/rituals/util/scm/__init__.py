# -*- coding: utf-8 -*-
""" rituals.util.scm – Source Code Management support.
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

from .git import GitProvider
from .null import NullProvider


# See "null.NullProvider" for the provider interface reference
SCM_PROVIDER = dict((i.key, i) for i in (GitProvider, NullProvider,))


def auto_detect(workdir):
    """ Return string signifying the SCM used in the given directory.

        Currently, 'git' is supported. Anything else returns 'unknown'.
    """
    # Any additions here also need a change to `SCM_PROVIDERS`!
    if os.path.isdir(os.path.join(workdir, '.git')) and os.path.isfile(os.path.join(workdir, '.git', 'HEAD')):
        return 'git'

    return 'unknown'


def provider(workdir, commit=True, **kwargs):
    """Factory for the correct SCM provider in `workdir`."""
    return SCM_PROVIDER[auto_detect(workdir)](workdir, commit=commit, **kwargs)
