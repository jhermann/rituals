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
import time
import shutil
import tempfile
import textwrap
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
from ..util.shell import capture

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


def watchdogctl(ctx, kill=False, verbose=True):
    """Control / check a running Sphinx autobuild process."""
    tries = 40 if kill else 0
    cmd = 'lsof -i TCP:{} -s TCP:LISTEN -S -Fp'.format(ctx.rituals.docs.watchdog.port)

    pid = capture(cmd, ignore_failures=True)
    while pid:
        assert pid.startswith('p'), "Standard lsof output expected"
        pid = int(pid[1:], 10)
        if verbose:
            ctx.run("ps uw {}".format(pid), echo=False)
            verbose = False

        tries -= 1
        if tries > 0:
            notify.info("Killing PID {}".format(pid))
            ctx.run("kill {}".format(pid), echo=False)
            time.sleep(.25)
        else:
            break

        pid = capture(cmd, ignore_failures=True)

    return pid or 0


@task(default=True, help={
    'browse': "Open index page in browser tab",
    'clean': "Start with a clean build area",
    'watchdog': "Start autobuild watchdog?",
    'kill': "Stop autobuild watchdog (and do nothing else)",
    'status': "Show autobuild watchdog process state",
    'opts': "Extra flags for Sphinx builder",
})
def sphinx(ctx, browse=False, clean=False, watchdog=False, kill=False, status=False, opts=''):
    """Build Sphinx docs."""
    cfg = config.load()

    if kill or status:
        if not watchdogctl(ctx, kill=kill):
            notify.info("No process bound to port {}".format(ctx.rituals.docs.watchdog.port))
        return

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
                pypandoc.convert(markdown, 'rst', outputfile=os.path.join(ctx.rituals.docs.sources, basename + '.rst'))

    # LICENSE file
    if os.path.exists('LICENSE'):
        with io.open('LICENSE', 'r') as inp:
            license_text = inp.read()
            _, copyright_text = cfg.project['long_description'].split('Copyright', 1)
            with io.open(os.path.join(ctx.rituals.docs.sources, 'LICENSE.rst'), 'w') as out:
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
                license_text = textwrap.dedent(license_text)
                license_text = '\n    '.join(license_text.splitlines())
                out.write('    {}\n'.format(license_text))

    # Build API docs
    if cfg.project.packages:
        cmd = ['sphinx-apidoc', '-o', 'api', '-f', '-M']
        for package in cfg.project.packages:
            if '.' not in package:
                cmd.append(cfg.srcjoin(package))
        with pushd(ctx.rituals.docs.sources):
            ctx.run(' '.join(cmd))

    # Auto build?
    cmd = ['sphinx-build', '-b', 'html']
    if opts:
        cmd.append(opts)
    cmd.extend(['.', ctx.rituals.docs.build])
    index_url = index_file = os.path.join(ctx.rituals.docs.sources, ctx.rituals.docs.build, 'index.html')
    if watchdog:
        watchdogctl(ctx, kill=True)
        cmd[0:1] = ['nohup', 'sphinx-autobuild']
        cmd.extend([
               '-H', ctx.rituals.docs.watchdog.host,
               '-p', '{}'.format(ctx.rituals.docs.watchdog.port),
               "-i'{}'".format('*~'),
               "-i'{}'".format('.*'),
               "-i'{}'".format('*.log'),
               ">watchdog.log", "2>&1", "&",
        ])
        index_url = "http://{}:{}/".format(ctx.rituals.docs.watchdog.host, ctx.rituals.docs.watchdog.port)

    # Build docs
    notify.info("Starting Sphinx {}build...".format('auto' if watchdog else ''))
    with pushd(ctx.rituals.docs.sources):
        ctx.run(' '.join(cmd))

    # Wait for watchdog to bind to listening port
    if watchdog:
        def activity(what=None, i=None):
            "Helper"
            if i is None:
                sys.stdout.write(what + '\n')
            else:
                sys.stdout.write(' {}  Waiting for {}\r'.format(r'\|/-'[i % 4], what or 'something'))
            sys.stdout.flush()

        for i in range(60):
            activity('server start', i)
            if watchdogctl(ctx):
                activity('OK')
                break
            time.sleep(1)
        else:
            activity('ERR')

        for i in range(60):
            activity('HTML index file', i)
            if os.path.exists(index_file):
                activity('OK')
                break
            os.utime(os.path.join(ctx.rituals.docs.sources, 'index.rst'), None)
            time.sleep(1)
        else:
            activity('ERR')

    # Open in browser?
    if browse:
        time.sleep(1)
        webbrowser.open_new_tab(index_url)


@task(help={
    'browse': "Open index page on successful upload",
    'pypi': "Upload to {}".format(PYPI_URL),
})
def upload(ctx, browse=False, pypi=True):
    """Upload built Sphinx docs."""
    cfg = config.load()

    if not pypi:
        notify.failure("I have no target to upload to!")
    html_dir = os.path.join(ctx.rituals.docs.sources, ctx.rituals.docs.build)
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


namespace = Collection.from_module(sys.modules[__name__], name='docs', config={'rituals': dict(
    docs = dict(
        sources = 'docs',
        build = '_build',
        watchdog = dict(
            host = '127.0.0.1',
            port = 8840,
        ),
    ),
)})
