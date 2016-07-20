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

import os
import sys

from . import Collection, task, exceptions
from .. import config
from ..util import antglob, notify, shell, add_dir2pypath


@task(default=True, help=dict(
    skip_tests="Do not check test modules",
    skip_root="Do not check scripts in project root",
    reports="Create extended report?",
))
def pylint(ctx, skip_tests=False, skip_root=False, reports=False):
    """Perform source code checks via pylint."""
    cfg = config.load()
    add_dir2pypath(cfg.project_root)
    if not os.path.exists(cfg.testjoin('__init__.py')):
        add_dir2pypath(cfg.testjoin())

    namelist = set()
    for package in cfg.project.get('packages', []):
        if '.' not in package:
            namelist.add(cfg.srcjoin(package))
    for module in cfg.project.get('py_modules', []):
        namelist.add(module + '.py')

    if not skip_tests:
        test_py = antglob.FileSet(cfg.testdir, '**/*.py')
        test_py = [cfg.testjoin(i) for i in test_py]
        if test_py:
            namelist |= set(test_py)

    if not skip_root:
        root_py = antglob.FileSet('.', '*.py')
        if root_py:
            namelist |= set(root_py)

    namelist = set([i[len(os.getcwd())+1:] if i.startswith(os.getcwd() + os.sep) else i for i in namelist])
    cmd = 'pylint'
    cmd += ' "{}"'.format('" "'.join(sorted(namelist)))
    cmd += ' --reports={0}'.format('y' if reports else 'n')
    for cfgfile in ('.pylintrc', 'pylint.rc', 'pylint.cfg', 'project.d/pylint.cfg'):
        if os.path.exists(cfgfile):
            cmd += ' --rcfile={0}'.format(cfgfile)
            break
    try:
        shell.run(cmd, report_error=False, runner=ctx.run)
        notify.info("OK - No problems found by pylint.")
    except exceptions.Failure as exc:
        # Check bit flags within pylint return code
        if exc.result.return_code & 32:
            # Usage error (internal error in this code)
            notify.error("Usage error, bad arguments in {}?!".format(repr(cmd)))
            raise
        else:
            bits = {
                1: "fatal",
                2: "error",
                4: "warning",
                8: "refactor",
                16: "convention",
            }
            notify.warning("Some messages of type {} issued by pylint.".format(
                ", ".join([text for bit, text in bits.items() if exc.result.return_code & bit])
            ))
            if exc.result.return_code & 3:
                notify.error("Exiting due to fatal / error message.")
                raise


namespace = Collection.from_module(sys.modules[__name__], name='check')
