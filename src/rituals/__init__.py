# -*- coding: utf-8 -*-
# pylint: disable=bad-whitespace
"""
    Common tasks for 'Invoke' that are needed again and again.

    The ``rituals`` package provides PyInvoke tasks that work for any
    project, based on its project metadata, to automate common
    developer chores like 'clean', 'build', 'dist', 'test', 'check',
    and 'release-prep' (for the moment).

    The guiding principle for these tasks is to strictly separate
    low-level tasks for building and installing (via ``setup.py``) from
    high-level convenience tasks a developer uses (via ``tasks.py``).
    Invoke tasks can use Setuptools ones as building blocks, but
    never the other way 'round – this avoids bootstrapping head-
    aches during package installations using ``pip``.

    The easiest way to get a working project based on ``rituals`` is
    the ``py-generic-project`` cookiecutter template. That way you have
    a working project skeleton within minutes that is fully equipped,
    with all aspects of bootstrapping, building, testing, quality
    checks, continuous integration, documentation, and releasing
    covered. See here for more:

        https://github.com/Springerle/py-generic-project


    Copyright ⓒ  2015 - 2019 Jürgen Hermann

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
from __future__ import absolute_import, unicode_literals, print_function

__url__             = 'https://github.com/jhermann/rituals'
__version__         = '0.4.1'
__license__         = 'GPL v2'
__author__          = 'Jürgen Hermann'
__author_email__    = 'jh@web.de'
__keywords__        = 'invoke automation tasks release deploy distribute publish'
