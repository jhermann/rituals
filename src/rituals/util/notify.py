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

import sys

from invoke import exceptions

ECHO = True


def banner(msg):
    """Emit a banner just like Invoke's `run(…, echo=True)`."""
    if RUN_ECHO:
        sys.stdout.flush()
        print("\033[1;7;32;40m{}\033[0m".format(msg))
        sys.stdout.flush()


def info(msg):
    """Emit a normal message."""
    sys.stdout.flush()
    print(msg)
    sys.stdout.flush()


def warning(msg):
    """Emit a warning message."""
    sys.stdout.flush()
    print("\033[1;7;33;40mWARNING: {}\033[0m".format(msg))
    sys.stdout.flush()


def error(msg):
    """Emit an error message to stderr."""
    sys.stdout.flush()
    sys.stderr.flush()
    sys.stderr.write("\033[1;37;41mERROR: {}\033[0m\n".format(msg))
    sys.stderr.flush()


def failure(msg):
    """Emit a fatal message and exit."""
    error(msg)
    raise exceptions.Exit(1)
