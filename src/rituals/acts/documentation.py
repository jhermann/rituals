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
import re
import sys
import time
import shutil
import tempfile
import textwrap
import subprocess
import webbrowser
from contextlib import contextmanager

try:
    from configparser import ConfigParser, Error as ConfigError
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser, Error as ConfigError  # pylint: disable=import-error

import requests

from . import Collection, task
from .. import config
from ..util import notify
from ..util.filesys import pushd
from ..util.shell import capture


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
    cmd = 'lsof -i TCP:{} -s TCP:LISTEN -S -Fp 2>/dev/null'.format(ctx.rituals.docs.watchdog.port)

    pidno = 0
    pidinfo = capture(cmd, ignore_failures=True)
    while pidinfo:
        pidline = next(iter(filter(None, [re.match(r'^p(\d+)$', x) for x in pidinfo.splitlines()])))
        if not pidline:
            raise ValueError("Standard lsof output expected (got {!r})".format(pidinfo))
        pidno = int(pidline.group(1), 10)
        if verbose:
            ctx.run("ps uw {}".format(pidno), echo=False)
            verbose = False

        tries -= 1
        if tries <= 0:
            break
        else:
            try:
                os.kill(pidno, 0)
            except ProcessLookupError:
                break
            else:
                notify.info("Killing PID {}".format(pidno))
                ctx.run("kill {}".format(pidno), echo=False)
                time.sleep(.25)

        pid = capture(cmd, ignore_failures=True)

    return pidno


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
            try:
                _, copyright_text = cfg.project['long_description'].split('Copyright', 1)
            except (KeyError, ValueError):
                copyright_text = cfg.project.get('license', 'N/A')
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
    if cfg.project.get('packages') and str(ctx.rituals.docs.apidoc).lower()[:1] in 't1y':
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
        ctx.run(' '.join(cmd), pty=not watchdog)

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

        # trigger first build
        if os.path.exists(os.path.join(ctx.rituals.docs.sources, 'index.rst')):
            os.utime(os.path.join(ctx.rituals.docs.sources, 'index.rst'), None)

        for i in range(60):
            activity('HTML index file', i)
            if os.path.exists(index_file):
                activity('OK')
                break
            time.sleep(1)
        else:
            activity('ERR')

    # Open in browser?
    if browse:
        time.sleep(1)
        webbrowser.open_new_tab(index_url)


@task(help={
    'no-publish': "Do not publish to Confluence, just build",
    'clean': "Start with a clean build area",
    'opts': "Extra flags for Sphinx builder",
})
def confluence(ctx, no_publish=False, clean=False, opts=''):
    """Build Sphinx docs and publish to Confluence."""
    cfg = config.load()

    if clean:
        ctx.run("invoke clean --docs")

    cmd = ['sphinx-build', '-b', 'confluence']
    cmd.extend(['-E', '-a'])  # force a full rebuild
    if opts:
        cmd.append(opts)
    cmd.extend(['.', ctx.rituals.docs.build + '_cf'])
    if no_publish:
        cmd.extend(['-Dconfluence_publish=False'])

    # Build docs
    notify.info("Starting Sphinx build...")
    with pushd(ctx.rituals.docs.sources):
        ctx.run(' '.join(cmd), pty=True)

try:
    import sphinxcontrib.confluencebuilder
except ImportError:
    del confluence


class DocsUploader():
    """Helper to perform an upload of pre-built docs."""

    def __init__(self, ctx, cfg, target):
        self.ctx = ctx
        self.cfg = cfg
        self.target = target or ctx.rituals.docs.upload.method
        self.params = getattr(ctx.rituals.docs.upload.targets, self.target, None)

        if self.params is None:
            notify.failure("Unknown upload target '{}'!".format(self.target))
        if not self.params.get('url'):
            notify.failure("You must provide an upload URL for target '{}', e.g. via the environment:\n"
                           "    export INVOKE_RITUALS_DOCS_UPLOAD_TARGETS_{}_URL='http://.../{{name}}-{{version}}.zip'"
                           .format(self.target, self.target.upper()))

    @contextmanager
    def _zipped(self, docs_base):
        """ Provide a zipped stream of the docs tree."""
        with pushd(docs_base):
            with tempfile.NamedTemporaryFile(prefix='pythonhosted-', delete=False) as ziphandle:
                pass
            zip_name = shutil.make_archive(ziphandle.name, 'zip')

        notify.info("Uploading {:.1f} MiB from '{}' to '{}'..."
                    .format(os.path.getsize(zip_name) / 1024.0, zip_name, self.target))
        with io.open(zip_name, 'rb') as zipread:
            try:
                yield zipread
            finally:
                os.remove(ziphandle.name)
                os.remove(ziphandle.name + '.zip')

    def _to_pypi(self, docs_base, release):
        """Upload to PyPI."""
        url = None
        with self._zipped(docs_base) as handle:
            reply = requests.post(self.params['url'], auth=get_pypi_auth(), allow_redirects=False,
                                  files=dict(content=(self.cfg.project.name + '.zip', handle, 'application/zip')),
                                  data={':action': 'doc_upload', 'name': self.cfg.project.name})
            if reply.status_code in range(200, 300):
                notify.info("{status_code} {reason}".format(**vars(reply)))
            elif reply.status_code == 301:
                url = reply.headers['location']
            else:
                data = self.cfg.copy()
                data.update(self.params)
                data.update(vars(reply))
                notify.error("{status_code} {reason} for POST to {url}".format(**data))
        return url

    def _to_webdav(self, docs_base, release):
        """Upload to WebDAV store."""
        try:
            git_path = subprocess.check_output('git remote get-url origin 2>/dev/null', shell=True)
        except subprocess.CalledProcessError:
            git_path = ''
        else:
            git_path = git_path.decode('ascii').strip()
            git_path = git_path.replace('http://', '').replace('https://', '').replace('ssh://', '')
            git_path = re.search(r'[^:/]+?[:/](.+)', git_path)
            git_path = git_path.group(1).replace('.git', '') if git_path else ''
        url = None
        with self._zipped(docs_base) as handle:
            url_ns = dict(name=self.cfg.project.name, version=release, git_path=git_path)
            reply = requests.put(self.params['url'].format(**url_ns),
                                 data=handle.read(), headers={'Accept': 'application/json'})
            if reply.status_code in range(200, 300):
                notify.info("{status_code} {reason}".format(**vars(reply)))
                try:
                    data = reply.json()
                except ValueError as exc:
                    notify.warning("Didn't get a JSON response! ({})".format(exc))
                else:
                    if 'downloadUri' in data:  # Artifactory
                        url = data['downloadUri'] + '!/index.html'
            elif reply.status_code == 301:
                url = reply.headers['location']
            else:
                data = self.cfg.copy()
                data.update(self.params)
                data.update(vars(reply))
                notify.error("{status_code} {reason} for PUT to {url}".format(**data))

        if not url:
            notify.warning("Couldn't get URL from upload response!")
        return url

    def upload(self, docs_base, release):
        """Upload docs in ``docs_base`` to the target of this uploader."""
        return getattr(self, '_to_' + self.target)(docs_base, release)


@task(help={
    'browse': "Open index page on successful upload",
    'target': "Upload target name (default: pypi)",
    'release': "Version for upload path (default: latest)",
})
def upload(ctx, browse=False, target=None, release='latest'):
    """Upload a ZIP of built docs (by default to PyPI, else a WebDAV URL)."""
    cfg = config.load()
    uploader = DocsUploader(ctx, cfg, target)

    html_dir = os.path.join(ctx.rituals.docs.sources, ctx.rituals.docs.build)
    if not os.path.isdir(html_dir):
        notify.failure("No HTML docs dir found at '{}'!".format(html_dir))

    url = uploader.upload(html_dir, release)
    notify.info("Uploaded docs to '{url}'!".format(url=url or 'N/A'))
    if url and browse:  # Open in browser?
        webbrowser.open_new_tab(url)


namespace = Collection.from_module(sys.modules[__name__], name='docs', config={'rituals': dict(
    docs = dict(
        sources = 'docs',
        build = '_build',
        apidoc = True,
        watchdog = dict(
            host = '127.0.0.1',
            port = 8840,
        ),
        upload = dict(
            method = 'pypi',
            targets = dict(
                pypi = dict(url='https://pypi.python.org/pypi'),
                webdav = dict(url=None),  # must be set in the environment
            ),
        ),
    ),
)})
