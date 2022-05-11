# -*- coding: utf-8 -*-
# pylint: disable=
""" Helpers for handling the build system and project metdata.

    This module is supposed to handle (most of) the differences
    between different build tools and config files used in projects.
"""
# Copyright ⓒ  2021 Jürgen Hermann
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
import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict

from munch import Munch as Bunch

from . import notify, shell
from .. import config


def project_meta(project_root=None):
    """ Read and return all project metadata.
    """
    root_dir = Path(project_root or config.get_project_root() or '.')
    if (root_dir / 'setup.py').exists():
        # this assumes an importable setup.py
        if root_dir not in sys.path:
            sys.path.append(root_dir)
        try:
            from setup import project # pylint: disable=no-name-in-module
        except ImportError:
            # Support another common metadata name found in real-world projects
            from setup import setup_args as project # pylint: disable=no-name-in-module
    elif (root_dir / 'pyproject.toml').exists():
        import toml

        pyproject = toml.load(root_dir / 'pyproject.toml')
        backend = pyproject['build-system']['build-backend']
        if backend.startswith('poetry.'):
            poetry = defaultdict(str)
            poetry.update(pyproject['tool']['poetry'])
            author = (poetry['authors'] or [''])[0]
            project = dict(
                name=poetry['name'],
                version=poetry['version'],
                author=author.split('<')[0].strip(),
                author_email=(re.findall(r'<([^>]*?)>', author or '<>') or [''])[0],
                license=poetry['license'],
                packages=[poetry['name'].replace('-', '_')],
                url=poetry['homepage'],
                description=poetry['description'],
            )
        else:
            raise NotImplementedError('Unknown build system')
    else:
        raise NotImplementedError('Unknown project setup')

    def parse_copyright(text):
        'Helper'
        line = [x for x in text.splitlines() if 'Copyright' in x][0]
        return line.replace('Copyright', '').strip()

    project = Bunch(project)
    if 'long_description' in project:
        project.copyright = parse_copyright(project.long_description)
    elif (root_dir / 'LICENSE').exists():
        text = (root_dir / 'LICENSE').read_text(encoding='utf8', errors='replace')
        project.copyright = parse_copyright(text)
    if 'copyright' not in project:
        raise NotImplementedError('Cannot determine copyright for this project')

    return project


def project_version():
    """ Determine project version.
    """
    root_dir = Path(config.get_project_root() or '.')
    if (root_dir / 'setup.py').exists():
        return shell.capture('python setup.py --version')
    else:
        raise NotImplementedError()


def build(run=subprocess.check_call):
    """ Build a project.
    """
    root_dir = Path(config.get_project_root() or '.')
    if (root_dir / 'setup.py').exists():
        run("python setup.py build", shell=True)
    else:
        raise NotImplementedError()
