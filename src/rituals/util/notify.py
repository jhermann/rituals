# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
""" Log notification messages to console.
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

import sys

ECHO = True


def _flush():
    """Flush all console output."""
    sys.stdout.flush()
    sys.stderr.flush()


def banner(msg):
    """Emit a banner just like Invoke's `run(…, echo=True)`."""
    if ECHO:
        _flush()
        sys.stderr.write("\033[1;7;32;40m{}\033[0m\n".format(msg))
        sys.stderr.flush()


def info(msg):
    """Emit a normal message."""
    _flush()
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def warning(msg):
    """Emit a warning message."""
    _flush()
    sys.stderr.write("\033[1;7;33;40mWARNING: {}\033[0m\n".format(msg))
    sys.stderr.flush()


def error(msg):
    """Emit an error message to stderr."""
    _flush()
    sys.stderr.write("\033[1;37;41mERROR: {}\033[0m\n".format(msg))
    sys.stderr.flush()


def failure(msg):
    """Emit a fatal message and exit."""
    error(msg)
    sys.exit(1)
