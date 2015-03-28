# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, superfluous-parens, wildcard-import
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

from invoke import run, task

from rituals.util import notify

__all__ = ['devpi_refresh']


@task(name='devpi-refresh', help=dict(
    requirement="Refresh from the given requirements file (default: 'dev-requirements.txt')",
))
def devpi_refresh(requirement='dev-requirements.txt'):
    """Refresh 'devpi' PyPI links for the given requirements file."""
    import requests
    from pip.req.req_file import parse_requirements
    from pip.download import PipSession

    cmd = 'devpi use --urls'
    lines = run(cmd, hide='out', echo=False).stdout.splitlines()
    for line in lines:
        line, base_url = line.split(':', 1)
        if line.strip() == 'simpleindex':
            base_url = base_url.strip().rstrip('/')
            break
    else:
        notify.failure("Cannot find simpleindex URL in '{}' output:\n    {}".format(
            cmd, '\n    '.join(lines),
        ))

    notify.banner("Refreshing devpi links for {}".format(base_url))

    reqs = set(i.name for i in parse_requirements(requirement, session=PipSession()))
    for req in sorted(reqs):
        url = "{}/{}/refresh".format(base_url, req)
        response = requests.post(url)
        if response.status_code not in (200, 302):
            notify.warning("Failed to refresh {}: {} {}".format(url, response.status_code, response.reason))
        else:
            notify.info("{:>{width}}: {} {}".format(
                req, response.status_code, response.reason, width=4 + max(len(i) for i in reqs),
            ))
