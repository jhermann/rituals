#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" rituals – Common tasks for 'Invoke' that are needed again and again.

    Copyright ⓒ  2015 Jürgen Hermann

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 2 as
    published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    The full LICENSE file and source are available at
        https://github.com/jhermann/rituals
"""
import os
import re
import sys

# Project data (the rest is parsed from __init__.py and other project files)
name = 'rituals'

# Import setuptools
try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand
except ImportError, exc:
    raise RuntimeError("Cannot install '{0}', setuptools is missing ({1})".format(name, exc))

# Helpers
project_root = os.path.abspath(os.path.dirname(__file__))

def srcfile(*args):
    "Helper for path building."
    return os.path.join(*((project_root,) + args))

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import locally, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        if errno:
            sys.exit(errno)

def _build_metadata():
    "Return project's metadata as a dict."
    # Handle metadata in package source
    expected_keys = ('url', 'version', 'license', 'author', 'author_email', 'long_description')
    metadata = {}
    with open(srcfile('src', name, '__init__.py')) as handle:
        pkg_init = handle.read()
        # Get default long description from docstring
        metadata['long_description'] = re.search(r'^"""(.+?)^"""$', pkg_init, re.DOTALL|re.MULTILINE).group(1).strip()
        for line in pkg_init.splitlines():
            match = re.match(r"""^__({0})__ += (?P<q>['"])(.+?)(?P=q)$""".format('|'.join(expected_keys)), line)
            if match:
                metadata[match.group(1)] = match.group(3)

    if not all(i in metadata for i in expected_keys):
        raise RuntimeError("Missing or bad metadata in '{0}' package".format(name))

    # Load requirements files
    requirements_files = dict(
        install = 'requirements.txt',
        setup = 'setup-requirements.txt',
        test = 'test-requirements.txt',
    )
    requires = {}
    for key, filename in requirements_files.iteritems():
        requires[key] = []
        if os.path.exists(srcfile(filename)):
            with open(srcfile(filename), 'r') as handle:
                for line in handle:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if line.startswith('-e'):
                            line = line.split()[1].split('#egg=')[1]
                        requires[key].append(line)
    if 'pytest' not in requires['test']:
        requires['test'].append('pytest')

    # Complete project metadata
    with open(srcfile('classifiers.txt'), 'r') as handle:
        classifiers = [i.strip() for i in handle if i.strip() and not i.startswith('#')]

    metadata.update(dict(
        name = name,
        description = metadata['long_description'].split('.')[0],
        url = metadata['url'],
        package_dir = {'': 'src'},
        packages = find_packages(srcfile('src'), exclude=['tests']),
        zip_safe = False,
        include_package_data = True,
        install_requires = requires['install'],
        setup_requires = requires['setup'],
        tests_require =  requires['test'],
        classifiers = classifiers,
        cmdclass = dict(
            test = PyTest,
        ),
    ))
    return metadata

# Ensure "setup.py" is importable by other tools, to access the project's metadata
project = _build_metadata()
__all__ = ['project', 'project_root', 'srcfile']
if __name__ == '__main__':
    setup(**project)
