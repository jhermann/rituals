# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import, missing-docstring, redefined-outer-name, invalid-name, no-self-use
# pylint: disable=unused-wildcard-import, ungrouped-imports
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
from __future__ import absolute_import, unicode_literals, print_function

import os
import shutil
import tempfile
import unittest
from os.path import join

import pytest

from rituals.util import antglob
from rituals.util.antglob import *


class Glob2reTest(unittest.TestCase):

    def test_antglob_star_import_does_not_include_glob2re(self):
        assert 'glob2re' not in globals()

    def test_star_converts_to_non_slash_sequences(self):
        assert antglob.glob2re('a*b') == 'a[^/]*b'
        assert antglob.glob2re('a*b*') == 'a[^/]*b[^/]*'

    def test_charsets_are_left_intact(self):
        assert antglob.glob2re('[abc]') == '[abc]'

    def test_backslash_and_plus_are_properly_escaped(self):
        assert antglob.glob2re('\\') == r'\\'
        assert antglob.glob2re('+') == r'\+'


class ParseGlobTest(unittest.TestCase):

    def test_antglob_star_import_does_not_include_parse_glob(self):
        assert 'parse_glob' not in globals()

    def test_empty_inputs_create_an_empty_output(self):
        assert not list(antglob.parse_glob(None))
        assert not list(antglob.parse_glob(''))

    def test_twin_star_translates_to_null_match_or_non_empty_sequence_plus_slash(self):
        assert list(antglob.parse_glob('a/**/b')) == ['a/', '(|.+/)', 'b']

    def test_path_parts_have_a_trailing_slash(self):
        assert list(antglob.parse_glob('a/b/')) == ['a/', 'b/', '']

    def test_embedded_star_in_path_part_matches_non_slash_middle(self):
        assert list(antglob.parse_glob('a*b/c')) == ['a[^/]*b/', 'c']

    def test_absolute_paths_emit_a_starting_slash(self):
        assert list(antglob.parse_glob('/root')) == ['/', 'root']


@pytest.fixture(scope='module')
def root(request):
    """ Root of filesystem layout for tests.

        ./foo/
        ./foo/bar/
        ./foo/bar/.hidden/
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

    dir_foo = join(rootpath, "foo")
    dir_bar = join(dir_foo, "bar")
    dir_baz = join(dir_bar, "baz")
    hidden = join(dir_bar, ".hidden")
    os.makedirs(dir_baz)
    os.makedirs(hidden)

    new = (
        join(rootpath, "zero.py"),
        join(rootpath, "zero"),
        join(dir_foo, "one.py"),
        join(dir_foo, "one"),
        join(dir_bar, "two.py"),
        join(dir_bar, "two"),
        join(dir_baz, "three.py"),
        join(dir_baz, "three"),
        join(dir_baz, "..."),
    )

    for path in new:
        open(path, "a").close()

    return rootpath


def assert_sets_equal(s1, s2):
    """Helper to compare sets."""
    assert list(sorted(s1)) == list(sorted(s2))


def check_glob(root, pattern, expected):
    assert_sets_equal(antglob.FileSet(root, [antglob.includes(pattern)]), expected)


ALL_THE_PIES = ["zero.py", "foo/one.py", "foo/bar/two.py", "foo/bar/baz/three.py"]

def test_patterns_that_cause_an_empty_result(root):
    cases = (
        ("foo/blah/*.py", []),
        ("*.blah", []),
        ("**/hree.py", []),
        ("bar/foo/two.py", []),
    )

    for pattern, results in cases:
        check_glob(root, pattern, results)


def test_patterns_with_stars_and_twin_stars(root):
    cases = [
        ("*.py", ["zero.py"]),
        ("foo/*.py", ["foo/one.py"]),
        ("*/*", ["foo/one.py", "foo/one"]),
        ("**/*a*/**/*.py", ["foo/bar/two.py", "foo/bar/baz/three.py"])
    ]

    for pattern, results in cases:
        check_glob(root, pattern, results)


def test_twin_star_pattern_matches_root_files(root):
    root_py = set(antglob.FileSet(root, [antglob.includes('*.py')]))
    all_py = set(antglob.FileSet(root, [antglob.includes('**/*.py')]))
    assert len(root_py) == 1
    assert len(all_py) > 1
    assert root_py <= all_py


def test_direct_matches_for_plain_filenames_and_paths(root):
    cases = [
        ("zero.py", ["zero.py"]),
        ("foo/bar/baz/three.py", ["foo/bar/baz/three.py"]),
    ]

    for pattern, results in cases:
        check_glob(root, pattern, results)


def test_recursive_patterns_using_twin_stars_once_or_twice(root):
    cases = (
        ("**/...", ["foo/bar/baz/..."]),
        ("**/*.py", ALL_THE_PIES),
        ("**/baz/**/*.py", ["foo/bar/baz/three.py"]),
    )

    for pattern, results in cases:
        check_glob(root, pattern, results)


def test_multiple_combinations_of_includes_and_excludes(root):
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

    d2 = FileSet(root, [
        includes("**/*.py"),
        excludes("**/foo/"),
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
        (d2, ["zero.py"]),
        (e, ["zero.py", "foo/one.py"]),
    )

    for result, expected in cases:
        assert_sets_equal(result, expected)


def test_drivers_fileset_operator_combinations(root):
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


def test_directory_patterns_return_matches(root):
    assert_sets_equal(antglob.FileSet(root, "foo/"), ["foo/"])
    assert_sets_equal(antglob.FileSet(root, "**/baz/"), ["foo/bar/baz/"])
    assert_sets_equal(antglob.FileSet(root, "**/b*/"), ["foo/bar/", "foo/bar/baz/"])
    assert_sets_equal(antglob.FileSet(root, "**/.*/"), ["foo/bar/.hidden/"])
    assert_sets_equal(antglob.FileSet(root, "**/.*"), ["foo/bar/baz/..."])
    assert_sets_equal(antglob.FileSet(root, "*/"), ["foo/"])
    assert_sets_equal(antglob.FileSet(root, "*/*/*/"), ["foo/bar/.hidden/", "foo/bar/baz/"])


def test_glob_patterns_with_normal_char_sets(root):
    assert_sets_equal(antglob.FileSet(root, "**/bar/[.b]*/"), ["foo/bar/.hidden/", "foo/bar/baz/"])


def test_glob_patterns_with_inverted_char_sets(root):
    assert_sets_equal(antglob.FileSet(root, "**/baz/[^.]*"), ["foo/bar/baz/three", "foo/bar/baz/three.py"])
    assert_sets_equal(antglob.FileSet(root, "**/baz/[^t]*"), ["foo/bar/baz/..."])


def test_string_patterns_are_inclusive_by_default(root):
    assert list(antglob.FileSet(root, "*.py")) == ["zero.py"]


def test_lists_of_string_patterns_are_combined(root):
    patterns = ["*.py", "foo/bar/tw*", "foo/bar/*.py"]
    assert set(antglob.FileSet(root, patterns[:1])) == set(["zero.py"])
    assert set(antglob.FileSet(root, patterns)) == set(["zero.py", "foo/bar/two", "foo/bar/two.py"])
