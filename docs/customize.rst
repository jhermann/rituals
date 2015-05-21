..  documentation: customize

    Copyright ⓒ  2015 Jürgen Hermann

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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration Reference
=======================

.. note::

    In the following tables of configurations settings, the root namespace of
    'rituals' is implied, so to access them in a task you'd use ``ctx.rituals.‹name›``,
    and ``INVOKE_RITUALS_‹NAME›`` to define an environment variable.


.. _customize-release:

Options for 'release'
---------------------

The ``release.pex`` task has an ``--upload`` option to upload the created archive
to a WebDAV repository, e.g. a local `Artifactory`_ server or to `Bintray`_.
The best way to make this usable in each of your projects is to insert the base URL
of your Python repository into your shell environment as follows:

.. code:: sh

    export INVOKE_RITUALS_RELEASE_UPLOAD_BASEURL=\
    "http://repo.example.com/artifactory/pypi-releases-local/"


The following settings are used when building self-contained releases that integrate `eGenix PyRun`_.

=================== =========================================================
Name                Description
=================== =========================================================
pyrun.version       The version of *PyRun* to use (e.g. ``2.1.0``)
pyrun.python        The version of *Python* to use (``2.6``, ``2.7``,
                    or ``3.4``)
pyrun.ucs           Unicode code points size (``ucs2`` or ``ucs4``)
pyrun.platform      The platform ID (e.g. ``linux-x86_64``,
                    ``macosx-10.5-x86_64``)
pyrun.url           Download location URL pattern
=================== =========================================================

The ``pyrun.url`` value can be a local ``http[s]`` URL
of an `Artifactory`_ repository or some similar webserver, or else
a ``file://`` URL of a file system cache. Note that the basename of
the URL should be exactly as in the following example, i.e. unchanged
from the original download name.

.. code:: sh

    export INVOKE_RITUALS_PYRUN_URL="file://"\
    "$HOME/Downloads/egenix-pyrun-{version}-py{python}_{ucs}-{platform}.tgz"


.. _`Artifactory`: http://www.jfrog.com/open-source/#os-arti
.. _`Bintray`: https://bintray.com/
.. _`eGenix PyRun`: https://www.egenix.com/products/python/PyRun/
