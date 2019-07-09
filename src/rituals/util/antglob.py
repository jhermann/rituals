# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
""" Recursive globbing with ant-style syntax.
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
import re

from ._compat import string_types

# TODO: allow '?'
# TODO: matching for Windows? (need to canonize to forward slashes in 'root')

__all__ = ['FileSet', 'includes', 'excludes']


def glob2re(part):
    """Convert a path part to regex syntax."""
    return "[^/]*".join(
        re.escape(bit).replace(r'\[\^', '[^').replace(r'\[', '[').replace(r'\]', ']')
        for bit in part.split("*")
    )


def parse_glob(pattern):
    """Generate parts of regex transformed from glob pattern."""
    if not pattern:
        return

    bits = pattern.split("/")
    dirs, filename = bits[:-1], bits[-1]

    for dirname in dirs:
        if dirname == "**":
            yield  "(|.+/)"
        else:
            yield glob2re(dirname) + "/"

    yield glob2re(filename)


def compile_glob(spec):
    """Convert the given glob `spec` to a compiled regex."""
    parsed = "".join(parse_glob(spec))
    regex = "^{0}$".format(parsed)
    return re.compile(regex)


class Pattern():
    """A single pattern for either inclusion or exclusion."""

    def __init__(self, spec, inclusive):
        """Create regex-based pattern matcher from glob `spec`."""
        self.compiled = compile_glob(spec.rstrip('/'))
        self.inclusive = inclusive
        self.is_dir = spec.endswith('/')

    def __str__(self):
        """Return inclusiveness indicator and original glob pattern."""
        return ('+' if self.inclusive else '-') + self.compiled.pattern

    def matches(self, path):
        """Check this pattern against given `path`."""
        return bool(self.compiled.match(path))


class FileSet():
    """ Ant-style file and directory matching.

        Produces an iterator of all of the files that match the provided patterns.
        Note that directory matches must end with a slash, and if they're exclusions,
        they won't be scanned (which prunes anything in that directory that would
        otherwise match).

        Directory specifiers:
            **              matches zero or more directories.
            /               path separator.

        File specifiers:
            *               glob style wildcard.
            [chars]         inclusive character sets.
            [^chars]        exclusive character sets.

        Examples:
            **/*.py         recursively match all python files.
            foo/**/*.py     recursively match all python files in the 'foo' directory.
            *.py            match all the python files in the current directory.
            */*.txt         match all the text files in top-level directories.
            foo/**/*        all files under directory 'foo'.
            */              top-level directories.
            foo/            the directory 'foo' itself.
            **/foo/         any directory named 'foo'.
            **/.*           hidden files.
            **/.*/          hidden directories.
    """

    def __init__(self, root, patterns):
        if isinstance(patterns, string_types):
            patterns = [patterns]

        self.root = root
        self.patterns = [i if hasattr(i, 'inclusive') else includes(i) for i in patterns]

    def __repr__(self):
        return "<FileSet at {0} {1}>".format(repr(self.root), ' '.join(str(i) for i in self. patterns))

    def included(self, path, is_dir=False):
        """Check patterns in order, last match that includes or excludes `path` wins. Return `None` on undecided."""
        inclusive = None
        for pattern in self.patterns:
            if pattern.is_dir == is_dir and pattern.matches(path):
                inclusive = pattern.inclusive

        #print('+++' if inclusive else '---', path, pattern)
        return inclusive

    def __iter__(self):
        for path in self.walk():
            yield path

    def __or__(self, other):
        return set(self) | set(other)

    def __ror__(self, other):
        return self | other

    def __and__(self, other):
        return set(self) & set(other)

    def __rand__(self, other):
        return self & other

    def walk(self, **kwargs):
        """ Like `os.walk` and taking the same keyword arguments,
            but generating paths relative to the root.

            Starts in the fileset's root and filters based on its patterns.
            If ``with_root=True`` is passed in, the generated paths include
            the root path.
        """
        lead = ''
        if 'with_root' in kwargs and kwargs.pop('with_root'):
            lead = self.root.rstrip(os.sep) + os.sep

        for base, dirs, files in os.walk(self.root, **kwargs):
            prefix = base[len(self.root):].lstrip(os.sep)
            bits = prefix.split(os.sep) if prefix else []

            for dirname in dirs[:]:
                path = '/'.join(bits + [dirname])
                inclusive = self.included(path, is_dir=True)
                if inclusive:
                    yield lead + path + '/'
                elif inclusive is False:
                    dirs.remove(dirname)

            for filename in files:
                path = '/'.join(bits + [filename])
                if self.included(path):
                    yield lead + path


def includes(pattern):
    """A single inclusive glob pattern."""
    return Pattern(pattern, inclusive=True)


def excludes(pattern):
    """A single exclusive glob pattern."""
    return Pattern(pattern, inclusive=False)
