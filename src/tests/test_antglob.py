# -*- coding: utf-8 -*-
""" Tests for `rituals.util.antglob`.
"""
#
# The MIT License (MIT)
#
# Original source (2014-02-17) from https://github.com/zacherates/fileset.py
# Copyright (c) 2012 Aaron Maenpaa
#
# Modifications at https://github.com/jhermann/rituals
# Copyright ⓒ  2015 Jürgen Hermann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shutil
import tempfile
from os.path import join

import pytest

from rituals.util.antglob import *


@pytest.fixture(scope='module')
def root(request):
    """ Root of filesystem layout for tests.

        ./foo/
        ./foo/bar/
        ./foo/bar/baz/
        ./foo/bar/baz/...
        ./foo/bar/baz/three
        ./foo/bar/baz/three.py
        ./foo/bar/two
        ./foo/bar/two.py
        ./foo/one
        ./foo/one.py
        ./zero
        ./zero.py
    """
    rootpath = tempfile.mkdtemp()
    request.addfinalizer(lambda: shutil.rmtree(rootpath))

    foo = join(rootpath, "foo")
    bar = join(foo, "bar")
    baz = join(bar, "baz")
    os.makedirs(baz)

    new = (
        join(rootpath, "zero.py"),
        join(rootpath, "zero"),
        join(foo, "one.py"),
        join(foo, "one"),
        join(bar, "two.py"),
        join(bar, "two"),
        join(baz, "three.py"),
        join(baz, "three"),
        join(baz, "..."),
    )

    for path in new:
        open(path, "a").close()

    return rootpath


def assert_sets_equal(s1, s2):
    """Helper to compare sets."""
    assert list(sorted(s1)) == list(sorted(s2))


def check_glob(root, pattern, expected):
    assert_sets_equal(FileSet(root, [includes(pattern)]), expected)


ALL_THE_PIES = ["zero.py", "foo/one.py", "foo/bar/two.py", "foo/bar/baz/three.py"]

def test_empty(root):
    cases = (
        ("foo/blah/*.py", []),
        ("*.blah", []),
        ("**/hree.py", []),
        ("foo/", []),
        ("bar/foo/two.py", []),
    )

    for pattern, results in cases:
        check_glob(root, pattern, results)


def test_glob(root):
    cases = [
        ("*.py", ["zero.py"]),
        ("foo/*.py", ["foo/one.py"]),
        ("*/*", ["foo/one.py", "foo/one"]),
        ("**/*a*/**/*.py", ["foo/bar/two.py", "foo/bar/baz/three.py"])
    ]

    for pattern, results in cases:
        check_glob(root, pattern, results)


def test_exact(root):
    cases = [
        ("zero.py", ["zero.py"]),
        ("foo/bar/baz/three.py", ["foo/bar/baz/three.py"]),
    ]

    for pattern, results in cases:
        check_glob(root, pattern, results)


def test_recursive(root):
    cases = (
        ("**/...", ["foo/bar/baz/..."]),
        ("**/*.py", ALL_THE_PIES),
        ("**/baz/**/*.py", ["foo/bar/baz/three.py"]),
    )

    for pattern, results in cases:
        check_glob(root, pattern, results)


def test_multi(root):
    a = FileSet(root, [
        includes("*.py"),
        includes("*/*.py"),
    ])

    b = FileSet(root, [
        includes("**/zero*"),
        includes("**/one*"),
    ])

    c = FileSet(root, [
        includes("**/*"),
        excludes("**/*.py"),
        excludes("**/baz/*"),
    ])

    d = FileSet(root, [
        includes("**/*.py"),
        excludes("**/foo/**/*"),
        includes("**/baz/**/*.py"),
    ])

    e = FileSet(root, [
        includes("**/*.py"),
        excludes("**/two.py"),
        excludes("**/three.py"),
    ])

    cases = (
        (a, ["zero.py", "foo/one.py"]),
        (b, ["zero.py", "zero", "foo/one.py", "foo/one"]),
        (c, ["zero", "foo/one", "foo/bar/two"]),
        (d, ["zero.py", "foo/bar/baz/three.py"]),
        (e, ["zero.py", "foo/one.py"]),
    )

    for result, expected in cases:
        assert_sets_equal(result, expected)


def test_set(root):
    a = FileSet(root, [
        includes("**/*.py")
    ])

    b = FileSet(root, [
        includes("**/*"),
        excludes("**/bar/**/*"),
    ])

    c = FileSet(root, [])

    cases = (
        (a | b, ALL_THE_PIES + ["zero", "foo/one"]),
        (a & b, ["zero.py", "foo/one.py"]),
        (a | c, a),
        (a & c, []),
        (a | b | c, ALL_THE_PIES + ["zero", "foo/one"]),
        ((a | b) & c, []),
        (a & b & c, []),
    )

    for result, expected in cases:
        assert_sets_equal(result, expected)