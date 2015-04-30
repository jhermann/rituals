# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, bad-whitespace
""" 'docs' tasks.
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
import sys
import webbrowser

from invoke import Collection, ctask as task

from .. import config
from ..util import notify
from ..util.filesys import pushd


@task(default=True, help={
    'browse': "Open index page in browser tab",
    'opts': "Extra flags for Sphinx builder",
})
def sphinx(ctx, browse=False, opts=''):
    """Build Sphinx docs."""
    cfg = config.load()

    # Convert markdown files, if applicable
    for basename in ('README', 'CONTRIBUTING'):
        markdown = cfg.rootjoin(basename + '.md')
        if os.path.exists(markdown):
            try:
                import pypandoc
            except ImportError as exc:
                notify.warning("Can't import 'pandoc' ({})".format(exc))
                break
            else:
                pypandoc.convert(markdown, 'rst', outputfile=os.path.join(ctx.docs.sources, basename + '.rst'))

    # Build API docs
    cmd = ['sphinx-apidoc', '-o', 'api', '-f', '-M']
    for package in cfg.project.packages:
        if '.' not in package:
            cmd.append(cfg.srcjoin(package))
    with pushd(ctx.docs.sources):
        ctx.run(' '.join(cmd))

    # Build docs
    cmd = ['sphinx-build', '-b', 'html']
    if opts:
        cmd.append(opts)
    cmd.extend(['.', ctx.docs.build])
    with pushd(ctx.docs.sources):
        ctx.run(' '.join(cmd))

    # Open in browser?
    if browse:
        webbrowser.open_new_tab(os.path.join(ctx.docs.sources, ctx.docs.build, 'index.html'))


namespace = Collection.from_module(sys.modules[__name__], name='docs', config=dict(
    docs = dict(
        sources = 'docs',
        build = '_build',
    ),
))
