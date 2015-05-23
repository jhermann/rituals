..  documentation: usage

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

User's Manual
=============

Introduction
------------

“Rituals” is a task library for `Invoke <http://www.pyinvoke.org/>`_
that keeps the most common tasks you always need out of your project,
and makes them centrally maintained. This leaves your ``tasks.py`` small
and to the point, with only things specific to the project at hand.

The following lists the common task implementations that the
``rituals.easy`` module offers. See :ref:`below <import-rituals-easy>`
on how to integrate them into your ``tasks.py``.

  * ``help`` – Default task, when invoked with no task names.
  * ``clean`` – Perform house-cleaning.
  * ``build`` – Build the project.
  * ``docs`` – Build the documentation.
  * ``test`` – Perform standard unittests.
  * ``check`` – Perform source code checks.
  * ``release.bump`` – Bump a development version.
  * ``release.dist`` – Distribute the project.
  * ``release.prep`` – Prepare for a release.
  * … and *many* more, see ``inv -l`` for a complete list.

The guiding principle for these tasks is to strictly separate low-level
tasks for building and installing (via ``setup.py``) from high-level
convenience tasks a developer uses (via ``invoke``). Invoke tasks can
use *Setuptools* ones as building blocks, but never the other way 'round –
this avoids any bootstrapping headaches during package installations.

Use ``inv -h ‹task›`` as usual to get details on the options of these
tasks.
The :doc:`tasks` explains them in more detail.
Look at the modules in
`rituals.acts <https://github.com/jhermann/rituals/blob/master/src/rituals/acts>`__
if you want to know every nuance of what these tasks do.

.. note::

    .. image:: _static/img/py-generic-project-logo.png
       :align: left

    The easiest way to get a working project using ``rituals`` is the
    `py-generic-project <https://github.com/Springerle/py-generic-project>`__
    cookiecutter archetype, which is tightly integrated with the tasks
    defined here.

    That way you have a working project skeleton
    within minutes that is fully equipped, with all aspects of building,
    testing, quality checks, continuous integration, documentation, and
    releasing covered.


.. _task-namespaces:

Provided Task Namespaces
^^^^^^^^^^^^^^^^^^^^^^^^

**TODO**


Basic Usage
-----------

.. _import-rituals-easy:

Add common tasks to your project's ``task.py``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add ``rituals`` to your ``dev-requirements.txt`` or a similar file, or
add it to ``setup_requires`` in your ``setup.py``. Then at the start of
your ``tasks.py``, use the following statement to define *all* tasks
that are considered standard:

.. code:: py

    from rituals.easy import *

Note that this defines Invoke's ``Collection`` and ``task`` identifiers,
the root ``namespace``\ with Ritual's default tasks, and some common
helpers (see the documentation for details). Of course, you can also do
more selective imports, or build your own Invoke namespaces with the
specific tasks you need.

.. warning::

    These tasks expect an importable ``setup.py`` that defines
    a ``project`` dict with the setup parameters, see
    `javaprops <https://github.com/Feed-The-Web/javaprops>`_ and
    `py-generic-project <https://github.com/Springerle/py-generic-project>`_
    for examples.

To refer to the current GitHub ``master`` branch, use a ``pip``
requirement like this::

    -e git+https://github.com/jhermann/rituals.git#egg=rituals


Change default project layout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, sources are expected in ``src/‹packagename›`` and tests in
``src/tests``.

You can change this by calling one of the following functions, directly
after the import from ``rituals.invoke_tasks``.

  * ``config.set_maven_layout()`` – Changes locations to
    ``src/main/python/‹packagename›`` and ``src/test/python``.
  * ``config.set_flat_layout()`` – Changes locations to ``‹packagename›``
    and ``tests``.


Change default project configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**TODO**
