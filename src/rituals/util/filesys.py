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
import re
import tempfile
from contextlib import contextmanager

import requests

from ._compat import urlparse, decode_filename



def pretty_path(path, _home_re=re.compile('^' + re.escape(os.path.expanduser('~') + os.sep))):
    """Prettify path for humans, and make it Unicode."""
    path = decode_filename(path)
    path = _home_re.sub('~' + os.sep, path)
    return path


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


# Copied from "rudiments.www"
@contextmanager
def url_as_file(url, ext=None):
    """
        Context manager that GETs a given `url` and provides it as a local file.

        The file is in a closed state upon entering the context,
        and removed when leaving it, if still there.

        To give the file name a specific extension, use `ext`;
        the extension can optionally include a separating dot,
        otherwise it will be added.

        Parameters:
            url (str): URL to retrieve.
            ext (str, optional): Extension for the generated filename.

        Yields:
            str: The path to a temporary file with the content of the URL.

        Raises:
            requests.RequestException: Base exception of ``requests``, see its
                docs for more detailed ones.

        Example:
            >>> import io, re, json
            >>> with url_as_file('https://api.github.com/meta', ext='json') as meta:
            ...     meta, json.load(io.open(meta, encoding='ascii'))['hooks']
            (u'/tmp/www-api.github.com-Ba5OhD.json', [u'192.30.252.0/22'])
    """
    if ext:
        ext = '.' + ext.strip('.')  # normalize extension
    url_hint = 'www-{}-'.format(urlparse(url).hostname or 'any')

    if url.startswith('file://'):
        url = os.path.abspath(url[len('file://'):])
    if os.path.isabs(url):
        with open(url, 'rb') as handle:
            content = handle.read()
    else:
        content = requests.get(url).content

    with tempfile.NamedTemporaryFile(suffix=ext or '', prefix=url_hint, delete=False) as handle:
        handle.write(content)

    try:
        yield handle.name
    finally:
        if os.path.exists(handle.name):
            os.remove(handle.name)
