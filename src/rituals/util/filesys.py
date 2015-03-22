# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
""" File system helpers.
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
from contextlib import contextmanager


@contextmanager
def pushd(path):
    """ A context that enters a given directory and restores the old state on exit.

        The original directory is returned as the context variable.
    """
    saved = os.getcwd()
    os.chdir(path)
    try:
        yield saved
    finally:
        os.chdir(saved)
