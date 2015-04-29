# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, superfluous-parens, bad-whitespace
""" Release tasks.
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
import zipfile
from contextlib import closing

import requests
from invoke import Collection, ctask as task
from bunch import Bunch

from .. import config
from ..util import notify, shell
from ..util.scm import provider as scm_provider
from ..util.shell import capture

PKG_INFO_MULTIKEYS = ('Classifier',)


def get_egg_info(cfg, verbose=False):
    """Call 'setup egg_info' and return the parsed meta-data."""
    result = Bunch()
    setup_py = cfg.rootjoin('setup.py')
    if not os.path.exists(setup_py):
        return result

    egg_info = shell.capture("python {} egg_info".format(setup_py), echo=True if verbose else None)
    for line in egg_info.splitlines():
        if line.endswith('PKG-INFO'):
            pkg_info_file = line.split(None, 1)[1]
            result['__file__'] = pkg_info_file
            with io.open(pkg_info_file, encoding='utf-8') as handle:
                lastkey = None
                for line in handle:
                    if line.lstrip() != line:
                        assert lastkey, "Bad continuation in PKG-INFO file '{}': {}".format(pkg_info_file, line)
                        result[lastkey] += '\n' + line
                    else:
                        lastkey, value = line.split(':', 1)
                        lastkey = lastkey.strip().lower().replace('-', '_')
                        value = value.strip()
                        if lastkey in result:
                            try:
                                result[lastkey].append(value)
                            except AttributeError:
                                result[lastkey] = [result[lastkey], value]
                        else:
                            result[lastkey] = value

    for multikey in PKG_INFO_MULTIKEYS:
        if not isinstance(result.get(multikey, []), list):
            result[multikey] = [result[multikey]]

    return result


@task(help=dict(
    verbose="Print version information as it is collected.",
    pypi="Do not create a local part for the PEP-440 version.",
))
def bump(ctx, verbose=False, pypi=False):
    """Bump a development version."""
    cfg = config.load()
    scm = scm_provider(cfg.project_root, commit=False, ctx=ctx)

    # Check for uncommitted changes
    if not scm.workdir_is_clean():
        notify.warning("You have uncommitted changes, will create a time-stamped version!")

    pep440 = scm.pep440_dev_version(verbose=verbose, non_local=pypi)

    # Rewrite 'setup.cfg'  TODO: refactor to helper, see also release-prep
    # with util.rewrite_file(cfg.rootjoin('setup.cfg')) as lines:
    #     ...
    setup_cfg = cfg.rootjoin('setup.cfg')
    if not pep440:
        notify.info("Working directory contains a release version!")
    elif os.path.exists(setup_cfg):
        with io.open(setup_cfg, encoding='utf-8') as handle:
            data = handle.readlines()
        changed = False
        for i, line in enumerate(data):
            if re.match(r"#? *tag_build *= *.*", line):
                verb, _ = data[i].split('=', 1)
                data[i] = '{}= {}\n'.format(verb, pep440)
                changed = True

        if changed:
            notify.info("Rewriting 'setup.cfg'...")
            with io.open(setup_cfg, 'w', encoding='utf-8') as handle:
                handle.write(''.join(data))
        else:
            notify.warning("No 'tag_build' setting found in 'setup.cfg'!")
    else:
        notify.warning("Cannot rewrite 'setup.cfg', none found!")

    if os.path.exists(setup_cfg):
        # Update metadata and print version
        egg_info = shell.capture("python setup.py egg_info", echo=True if verbose else None)
        for line in egg_info.splitlines():
            if line.endswith('PKG-INFO'):
                pkg_info_file = line.split(None, 1)[1]
                with io.open(pkg_info_file, encoding='utf-8') as handle:
                    notify.info('\n'.join(i for i in handle.readlines() if i.startswith('Version:')).strip())
        ctx.run("python setup.py -q develop", echo=True if verbose else None)


@task(help=dict(
    devpi="Upload the created 'dist' using 'devpi'",
    egg="Also create an EGG",
    wheel="Also create a WHL",
    auto="Create EGG for Python2, and WHL whenever possible",
))
def dist(ctx, devpi=False, egg=False, wheel=False, auto=True):
    """Distribute the project."""
    config.load()
    cmd = ["python", "setup.py", "sdist"]

    # Automatically create wheels if possible
    if auto:
        egg = sys.version_info.major == 2
        try:
            import wheel as _
            wheel = True
        except ImportError:
            wheel = False

    if egg:
        cmd.append("bdist_egg")
    if wheel:
        cmd.append("bdist_wheel")

    ctx.run("invoke clean --all build --docs test check")
    ctx.run(' '.join(cmd))
    if devpi:
        ctx.run("devpi upload dist/*")


@task(help=dict(
    upload="Upload the created archive to a WebDAV repository",
    opts="Extra flags for PEX",
))
def pex(ctx, upload=False, opts=''):
    """Package the project with PEX."""
    cfg = config.load()

    # Build and check release
    ctx.run(": invoke clean --all build test check")

    # Get full version
    pkg_info = get_egg_info(cfg)
    # from pprint import pprint; pprint(dict(pkg_info))
    version = pkg_info.version if pkg_info else cfg.project.version

    # Build a PEX for each console entry-point
    pex_files = []
    # from pprint import pprint; pprint(cfg.project.entry_points)
    for script in cfg.project.entry_points['console_scripts']:
        script, entry_point = script.split('=', 1)
        script, entry_point = script.strip(), entry_point.strip()
        pex_file = cfg.rootjoin('bin', '{}-{}.pex'.format(script, version))
        cmd = ['pex', '-r', cfg.rootjoin('requirements.txt'), cfg.project_root, '-c', script, '-o', pex_file]
        if opts:
            cmd.append(opts)
        ctx.run(' '.join(cmd))

        # Warn about non-portable stuff
        non_universal = set()
        with closing(zipfile.ZipFile(pex_file, mode="r")) as pex:
            for pex_name in pex.namelist():
                if pex_name.endswith('WHEEL') and '-py2.py3-none-any.whl' not in pex_name:
                    non_universal.add(pex_name.split('.whl')[0].split('/')[-1])
        if non_universal:
            notify.warning("Non-universal or native wheels in PEX '{}':\n    {}"
                           .format(pex_file.replace(os.getcwd(), '.'), '\n    '.join(sorted(non_universal))))
            envs = [i.split('-')[-3:] for i in non_universal]
            envs = {i[0]: i[1:] for i in envs}
            if len(envs) > 1:
                envs = {k: v for k, v in envs.items() if not k.startswith('py')}
            env_id = []
            for k, v in sorted(envs.items()):
                env_id.append(k)
                env_id.extend(v)
            env_id = '-'.join(env_id)
            new_pex_file = pex_file.replace('.pex', '-{}.pex'.format(env_id))
            notify.info("Renamed PEX to '{}'".format(os.path.basename(new_pex_file)))
            os.rename(pex_file, new_pex_file)
            pex_file = new_pex_file

        pex_files.append(pex_file)

    if not pex_files:
        notify.warning("No entry points found in project configuration!")
    elif upload:
        baseurl = ctx.release.upload.baseurl.rstrip('/')
        if not baseurl:
            notify.failure("No base URL provided for uploading!")

        for pex_file in pex_files:
            url = baseurl + '/' + ctx.release.upload.path.lstrip('/').format(
                name=cfg.project.name, version=cfg.project.version, filename=os.path.basename(pex_file))
            notify.info("Uploading to '{}'...".format(url))
            with io.open(pex_file, 'rb') as handle:
                reply = requests.put(url, data=handle.read())
                if reply.status_code in range(200, 300):
                    notify.info("{status_code} {reason}".format(**vars(reply)))
                else:
                    notify.warning("{status_code} {reason}".format(**vars(reply)))


@task(
    #pre=[
    #    # Fresh build
    #    call(clean, all=True),
    #    call(build, docs=True),

        # Perform quality checks
    #    call(test),
    #    call(check, reports=False),
    #],
    help=dict(
        commit="Commit any automatic changes and tag the release",
    ),
) # pylint: disable=too-many-branches
def prep(ctx, commit=True):
    """Prepare for a release."""
    cfg = config.load()
    scm = scm_provider(cfg.project_root, commit=commit, ctx=ctx)

    # Check for uncommitted changes
    if not scm.workdir_is_clean():
        notify.failure("You have uncommitted changes, please commit or stash them!")

    # TODO Check that changelog entry carries the current date

    # Rewrite 'setup.cfg'
    setup_cfg = cfg.rootjoin('setup.cfg')
    if os.path.exists(setup_cfg):
        with io.open(setup_cfg, encoding='utf-8') as handle:
            data = handle.readlines()
        changed = False
        for i, line in enumerate(data):
            if any(line.startswith(i) for i in ('tag_build', 'tag_date')):
                data[i] = '#' + data[i]
                changed = True
        if changed and commit:
            notify.info("Rewriting 'setup.cfg'...")
            with io.open(setup_cfg, 'w', encoding='utf-8') as handle:
                handle.write(''.join(data))
            scm.add_file('setup.cfg')
        elif changed:
            notify.warning("WOULD rewrite 'setup.cfg', but --no-commit was passed")
    else:
        notify.warning("Cannot rewrite 'setup.cfg', none found!")

    # Update metadata and command stubs
    ctx.run('python setup.py -q develop -U')

    # Build a clean dist and check version number
    version = capture('python setup.py --version')
    ctx.run('invoke clean --all build --docs release.dist')
    for distfile in os.listdir('dist'):
        trailer = distfile.split('-' + version)[1]
        trailer, _ = os.path.splitext(trailer)
        if trailer and trailer[0] not in '.-':
            notify.failure("The version found in 'dist' seems to be"
                           " a pre-release one! [{}{}]".format(version, trailer))

    # Commit changes and tag the release
    scm.commit(ctx.release.commit.message.format(version=version))
    scm.tag(ctx.release.tag.name.format(version=version), ctx.release.tag.message.format(version=version))


namespace = Collection.from_module(sys.modules[__name__], name='release', config=dict(
    release = dict(
        commit = dict(message = ':package: Release v{version}'),
        tag = dict(name = 'v{version}', message = 'Release v{version}'),
        upload = dict(baseurl = '', path='{name}/{version}/{filename}'),
    ),
))
