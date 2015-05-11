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

import io
import os
import sys
import shutil
import tempfile
import webbrowser

try:
    from configparser import ConfigParser, Error as ConfigError
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser, Error as ConfigError  # pylint: disable=import-error

import requests
from invoke import Collection, ctask as task

from .. import config
from ..util import notify
from ..util.filesys import pushd

PYPI_URL = 'https://pypi.python.org/pypi'


def get_pypi_auth(configfile='~/.pypirc'):
    """Read auth from pip config."""
    pypi_cfg = ConfigParser()
    if pypi_cfg.read(os.path.expanduser(configfile)):
        try:
            user = pypi_cfg.get('pypi', 'username')
            pwd = pypi_cfg.get('pypi', 'password')
            return user, pwd
        except ConfigError:
            notify.warning("No PyPI credentials in '{}',"
                           " will fall back to '~/.netrc'...".format(configfile))
    return None


@task(default=True, help={
    'browse': "Open index page in browser tab",
    'clean': "Start with a clean build area",
    'opts': "Extra flags for Sphinx builder",
})
def sphinx(ctx, browse=False, clean=False, opts=''):
    """Build Sphinx docs."""
    cfg = config.load()

    if clean:
        ctx.run("invoke clean --docs")

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

    # LICENSE file
    if os.path.exists('LICENSE'):
        with io.open('LICENSE', 'r') as inp:
            license_text = inp.read()
            _, copyright_text = cfg.project['long_description'].split('Copyright', 1)
            with io.open(os.path.join(ctx.docs.sources, 'LICENSE.rst'), 'w') as out:
                out.write(
                    'Software License\n'
                    '================\n'
                    '\n'
                    '    Copyright {}\n'
                    '\n'
                    'Full License Text\n'
                    '-----------------\n'
                    '\n'
                    '::\n'
                    '\n'
                    .format(copyright_text)
                )
                out.write(license_text)

    # Build API docs
    if cfg.project.packages:
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


@task(help={
    'browse': "Open index page on successful upload",
    'pypi': "Upload to {}".format(PYPI_URL),
})
def upload(ctx, browse=False, pypi=True):
    """Upload built Sphinx docs."""
    cfg = config.load()

    if not pypi:
        notify.failure("I have no target to upload to!")
    html_dir = os.path.join(ctx.docs.sources, ctx.docs.build)
    if not os.path.isdir(html_dir):
        notify.failure("No HTML docs dir found at '{}'!".format(html_dir))

    if pypi:
        with pushd(html_dir):
            with tempfile.NamedTemporaryFile(prefix='pythonhosted-', delete=False) as ziphandle:
                pass
            zip_name = shutil.make_archive(ziphandle.name, 'zip')

        notify.info("Uploading {:.1f} MiB from '{}'..."
                    .format(os.path.getsize(zip_name) / 1024.0, zip_name))
        with io.open(zip_name, 'rb') as zipread:
            try:
                reply = requests.post(PYPI_URL, auth=get_pypi_auth(), allow_redirects=False,
                              files=dict(content=(cfg.project.name + '.zip', zipread, 'application/zip')),
                              data={':action': 'doc_upload', 'name': cfg.project.name})
                if reply.status_code in range(200, 300):
                    notify.info("{status_code} {reason}".format(**vars(reply)))
                elif reply.status_code == 301:
                    url = reply.headers['location']
                    notify.info("Uploaded docs to '{url}'!".format(url=url))

                    # Open in browser?
                    if browse:
                        webbrowser.open_new_tab(url)
                else:
                    notify.error("{status_code} {reason}".format(**vars(reply)))

            finally:
                pass #os.remove(ziphandle.name)


namespace = Collection.from_module(sys.modules[__name__], name='docs', config=dict(
    docs = dict(
        sources = 'docs',
        build = '_build',
    ),
))
