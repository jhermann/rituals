# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, bad-whitespace
""" 'devpi' tasks.
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

#import os
import sys
#import warnings

from . import Collection, task
from ..util import notify


DEFAULT_REQUIREMENTS = 'dev-requirements.txt'


def get_devpi_url(ctx):
    """Get currently used 'devpi' base URL."""
    cmd = 'devpi use --urls'
    lines = ctx.run(cmd, hide='out', echo=False).stdout.splitlines()
    for line in lines:
        try:
            line, base_url = line.split(':', 1)
        except ValueError:
            notify.warning('Ignoring "{}"!'.format(line))
        else:
            if line.split()[-1].strip() == 'simpleindex':
                return base_url.split('\x1b')[0].strip().rstrip('/')

    raise LookupError("Cannot find simpleindex URL in '{}' output:\n    {}".format(
        cmd, '\n    '.join(lines),
    ))


# XXX: broken due to internal pip changes, must be rewritten to command calls or other libs
#@task(help=dict(
#    requirement="Refresh from the given requirements file (default: {})".format(DEFAULT_REQUIREMENTS),
#    name="Refresh a specific package",
#    installed="Refresh all installed packages",
#))  # pylint: disable=too-many-locals
#def refresh(ctx, requirement='', name='', installed=False):
#    """Refresh 'devpi' PyPI links."""
#    import requests
#    from pip import get_installed_distributions
#    from pip.download import PipSession
#    from pip.req.req_file import parse_requirements

#    with warnings.catch_warnings():
#        warnings.simplefilter('once')

#        # If no option at all is given, default to using 'dev-requirements.txt'
#        if not (requirement or name or installed):
#            requirement = ctx.rituals.devpi.requirements or DEFAULT_REQUIREMENTS
#            if not os.path.exists(requirement):
#                requirement = 'requirements.txt'

#        # Get 'devpi' URL
#        try:
#            base_url = get_devpi_url(ctx)
#        except LookupError as exc:
#            notify.failure(exc.args[0])
#        notify.banner("Refreshing devpi links on {}".format(base_url))

#        # Assemble requirements
#        reqs = set(('pip', 'setuptools', 'wheel'))  # always refresh basics
#        if requirement:
#            reqs |= set(i.name for i in parse_requirements(requirement, session=PipSession()))
#        if name:
#            reqs |= set([name])
#        if installed:
#            installed_pkgs = get_installed_distributions(local_only=True, skip=['python'])
#            reqs |= set(i.project_name for i in installed_pkgs)
#        reqs = [i for i in reqs if i]  # catch flukes

#        for req in sorted(reqs):
#            url = "{}/{}/refresh".format(base_url, req)
#            response = requests.post(url)
#            if response.status_code not in (200, 302):
#                notify.warning("Failed to refresh {}: {} {}".format(url, response.status_code, response.reason))
#            else:
#                notify.info("{:>{width}}: {} {}".format(
#                    req, response.status_code, response.reason, width=4 + max(len(i) for i in reqs),
#                ))

#        lines = ctx.run('pip list --local --outdated', hide='out', echo=False).stdout.splitlines()
#        if lines:
#            notify.banner("Outdated packages")
#            notify.info('    ' + '\n    '.join(sorted(lines)))


namespace = Collection.from_module(sys.modules[__name__], config={'rituals': dict(
    devpi = dict(
        requirements = DEFAULT_REQUIREMENTS,
    ),
)})
