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

Please read `Invoke's Configuration Guide`_ on the concepts and basic mechanisms
of its hierarchy of configuration files, environment variables, task namespaces
and CLI flags.
This reference guide lists the configuration options specific to tasks provided by *Rituals*.

.. note::

    In the following tables of configurations settings, the root namespace of
    'rituals' is implied, so to access them in a task you'd use ``ctx.rituals.‹name›``,
    and ``INVOKE_RITUALS_‹NAME›`` to define an environment variable.


-----------------------------------------------------------------------------
General Options
-----------------------------------------------------------------------------

To make Python versions available that are not part of the host's default
installation, ``rituals.snakepits`` is used, e.g. when performing multi-environment
testing. The default is ``/opt/pyenv/bin:/opt/pyrun/bin``.

=================== =========================================================
Name                Description
=================== =========================================================
snakepits           Lookup path for Python interpreters
=================== =========================================================


.. _customize-test:

-----------------------------------------------------------------------------
Options for 'test'
-----------------------------------------------------------------------------

If one of the directories in ``rituals.snakepits`` exists, it's added to the
``PATH`` of ``tox``.


.. _customize-docs:

-----------------------------------------------------------------------------
Options for 'docs'
-----------------------------------------------------------------------------

The defaults for the ``docs`` task should almost always fit, but if you need
to change them, you can.

=================== =========================================================
Name                Description
=================== =========================================================
docs.sources        Documentation source folder (``docs``)
docs.build          Build area within the source folder (``_build``)
docs.watchdog.host  IP to bind ``sphinx-autobuild`` to (``127.0.0.1``)
docs.watchdog.port  Port to bind ``sphinx-autobuild`` to (``8840``)
=================== =========================================================


.. _customize-release:

-----------------------------------------------------------------------------
Options for 'release'
-----------------------------------------------------------------------------

When ``release.prep`` changes the project configuration for a release and then
tags the resulting changeset, the values from the following table are used for
messages and names.

======================= =====================================================
Name                    Description
======================= =====================================================
release.commit.message  Message used (``:package: Release v{version}``)
release.tag.name        Release tag (``v{version}``)
release.tag.message     Tag annotation (``Release v{version}``)
======================= =====================================================


The ``release.pex`` task has an ``--upload`` option to upload the created archive
to a WebDAV repository, e.g. a local `Artifactory`_ server or to `Bintray`_.
The best way to make this usable in each of your projects is to insert the base URL
of your Python repository into your shell environment:

.. code:: sh

    export INVOKE_RITUALS_RELEASE_UPLOAD_BASE_URL=\
    "http://repo.example.com/artifactory/pypi-releases-local/"

======================= =====================================================
Name                    Description
======================= =====================================================
release.upload.base_url WebDAV server end-point
release.upload.path     WebDAV path (``{name}/{version}/{filename}``)
======================= =====================================================


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
pyrun.base_url      Download location base URL pattern
pyrun.archive       Download location file name pattern
=================== =========================================================

The ``rituals.pyrun.base_url`` value can be a local ``http[s]`` URL
of an `Artifactory`_ repository or some similar webserver, or else
a ``file://`` URL of a file system cache. Note that you should keep the
unchanged name of the original download location, i.e. do not change
``rituals.pyrun.archive``. The location patterns can contain the ``pyrun``
settings as placeholders, e.g. ``{version}``.

This sets a local download cache:

.. code:: sh

    export INVOKE_RITUALS_PYRUN_BASE_URL="file://$HOME/Downloads"

You have to download the *PyRun* releases you plan to use to that directory,
using your browser or ``curl``.


.. _customize-devpi:

-----------------------------------------------------------------------------
Options for 'devpi'
-----------------------------------------------------------------------------

When you call the ``devpi.refresh`` task without any option, the value of
``rituals.devpi.requirements`` is the name of the file parsed for the list
of packages to refresh in the active ``devpi`` server. It defaults to
``dev-requirements.txt``.

=================== =========================================================
Name                Description
=================== =========================================================
devpi.requirements  Name of requirements file to use for refreshing
=================== =========================================================


.. _`Invoke's Configuration Guide`: https://invoke.readthedocs.org/en/latest/concepts/configuration.html
.. _`Artifactory`: http://www.jfrog.com/open-source/#os-arti
.. _`Bintray`: https://bintray.com/
.. _`eGenix PyRun`: https://www.egenix.com/products/python/PyRun/
