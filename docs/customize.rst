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


.. _customize-release:

Options for 'release'
---------------------

The ``release.pex`` tasks has an ``--upload`` option to upload the created archive
to a WebDAV repository, e.g. a local `Artifactory`_ server or to `Bintray`_.
The best way to make this usable in each of your projects is to insert the base URL
of your Python repository into your shell environment as follows:

.. code:: sh

    export INVOKE_RITUALS_RELEASE_UPLOAD_BASEURL="http://repo.example.com/artifactory/pypi-releases-local/"


.. _`Artifactory`: http://www.jfrog.com/open-source/#os-arti
.. _`Bintray`: https://bintray.com/
