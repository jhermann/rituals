# -*- coding: utf-8 -*-
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

import os
import re
import sys
import itertools

# TODO: allow '?'
# TODO: prune excluded directories during walk()


def globify(part):
    return "[^/]*".join(re.escape(bit).replace(r'\[', '[').replace(r'\]', ']') for bit in part.split("*"))


class Pattern(object):
    def __init__(self, spec, inclusive):
        self.compiled = self.compile(spec)
        self.inclusive = inclusive

    def __str__(self):
        return self.compiled.pattern

    def compile(self, spec):
        parse = "".join(self.parse(spec))
        regex = "^{0}$".format(parse)
        return re.compile(regex)

    def parse(self, pattern):
        if not pattern:
            raise StopIteration

        bits = pattern.split("/")
        dirs, file = bits[:-1], bits[-1]

        for dir in dirs:
            if dir == "**":
                yield  "(|.+/)"

            else:
                yield globify(dir) + "/"

        yield globify(file)

    def matches(self, path):
        return self.compiled.match(path) is not None


class FileSet(object):
    """ Ant style file matching.

        Produces an iterator of all of the files that match the provided pattern.

        Directory specifiers:
            **          matches zero or more directories.
            *           matches any directory name.
            /           path separator.

        File specifiers:
            *           glob style wildcard.
            [chars]     character sets.

        Examples:
            **/*.py         recursively match all python files.
            foo/**/*.py     recursively match all python files in the foo/ directory.
            *.py            match all the python files in the current diretory.
            */*.txt         match all the text files in child directories.
    """

    def __init__(self, root, patterns):
        self.root = root
        self.patterns = patterns

    def included(self, path):
        """Check patterns in order, last match that includes or excludes `path` wins."""
        inclusive = False
        for pattern in self.patterns:
            if pattern.matches(path):
                inclusive = pattern.inclusive

        #print '+++' if inclusive else '---', path, pattern
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
        for base, dirs, files in os.walk(self.root, **kwargs):
            prefix = base[len(self.root):].lstrip(os.sep)
            bits = prefix.split(os.sep) if prefix else []

            for filename in files:
                path = '/'.join(bits + [filename])
                if self.included(path):
                    yield path

def includes(pattern):
    return Pattern(pattern, inclusive=True)

def excludes(pattern):
    return Pattern(pattern, inclusive=False)
