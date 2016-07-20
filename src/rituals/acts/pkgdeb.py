# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, bad-whitespace
""" 'deb' tasks.
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
import glob
import shutil

from . import Collection, task
from ..util import notify


@task(default=True, help=dict(
    dput="Host to upload to (use 'dput -H' to list them)",
    opts="Extra flags for package build",
))
def build(ctx, dput='', opts=''):
    """Build a DEB package."""
    # Get package metadata
    with io.open('debian/changelog', encoding='utf-8') as changes:
        metadata = re.match(r'^([^ ]+) \(([^)]+)\) ([^;]+); urgency=(.+)$', changes.readline().rstrip())
        if not metadata:
            notify.failure('Badly formatted top entry in changelog')
        name, version, _, _ = metadata.groups()

    # Build package
    ctx.run('dpkg-buildpackage {} {}'.format(ctx.rituals.deb.build.opts, opts))

    # Move created artifacts into "dist"
    if not os.path.exists('dist'):
        os.makedirs('dist')
    artifact_pattern = '{}?{}*'.format(name, re.sub(r'[^-_.a-zA-Z0-9]', '?', version))
    changes_files = []
    for debfile in glob.glob('../' + artifact_pattern):
        shutil.move(debfile, 'dist')
        if debfile.endswith('.changes'):
            changes_files.append(os.path.join('dist', os.path.basename(debfile)))
    ctx.run('ls -l dist/{}'.format(artifact_pattern))

    if dput:
        ctx.run('dput {} {}'.format(dput, ' '.join(changes_files)))


namespace = Collection.from_module(sys.modules[__name__], name='deb', config={'rituals': dict(
    deb = dict(
        build = dict(opts='-uc -us -b',),
    ),
)})
