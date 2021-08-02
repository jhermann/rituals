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

-----------------------------------------------------------------------------
Introduction
-----------------------------------------------------------------------------

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
convenience tasks a developer uses (via ``invoke``). *Invoke* tasks can
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
    `py-generic-project`_ cookiecutter archetype, which is tightly
    integrated with the tasks defined here.

    That way you have a working project skeleton
    within minutes that is fully equipped, with all aspects of building,
    testing, quality checks, continuous integration, documentation, and
    releasing covered.


.. _import-rituals-easy:

-----------------------------------------------------------------------------
Adding Rituals to Your Project
-----------------------------------------------------------------------------

First of all, include ``rituals`` as a dependency in your ``dev-requirements.txt``
or a similar file, to get a release from PyPI.
To refer to the current GitHub ``master`` branch instead, use a ``pip``
requirement like this::

    -e git+https://github.com/jhermann/rituals.git#egg=rituals

Then at the start of your ``tasks.py``, use the following statement to define
*all* tasks that are considered standard:

.. code:: py

    from rituals.easy import *

This works by defining the ``namespace`` identifier containing Ritual's default tasks.
Note that it also defines Invoke's ``Collection`` and ``task`` identifiers,
and some other common helpers assembled in :py:mod:`rituals.easy`.
`Rituals' own tasks.py`_ can serve as an example.

Of course, you may also do more selective imports, or build your own
*Invoke* namespaces with the specific tasks you need.

.. warning::

    These tasks expect an importable ``setup.py`` that defines
    a ``project`` dict with the setup parameters, see
    `rudiments <https://github.com/jhermann/rudiments>`_ and
    `py-generic-project`_ for examples. The needed changes are minimal:

    .. code:: py

        project = dict(  # this would usually be a setup(…) call
            name='…',
            ...
        )
        if __name__ == '__main__':
            setup(**project)


.. _`py-generic-project`: https://github.com/Springerle/py-generic-project


.. _task-namespaces:

-----------------------------------------------------------------------------
Task Namespaces
-----------------------------------------------------------------------------

The Root Namespace
^^^^^^^^^^^^^^^^^^

The tasks useful for any (Python) project are organized in a root namespace.
When you use the ``from rituals.easy import *`` statement, that also imports
this root namespace. By convention of *Invoke*, when the identifier ``namespace``
is defined, that one is taken instead of constructing one automatically from
all defined tasks.

It contains some fundamentals like ``clean``, and nested namespaces handling
specific topics. Examples of nested namespaces are ``test``, ``check``,
``docs``, and ``release``. See :doc:`tasks` for a complete list.

The root namespace has ``help`` as the default task, and
most nested namespaces also have a default with the most commonly performed
action. These default tasks are automatically aliased to the name of the
namespace, so for example ``docs.sphinx`` can also be called as ``docs``.


Adding Local Task Definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Having an explicit root namespace
means that within ``tasks.py``, you need to register your own tasks
using its ``add_task`` method, if you want them to be
available as top-level names:

.. code:: py

    @task
    def my_own_task(ctx):
        """Something project-specific."""
        ...

    namespace.add_task(my_own_task)

`Rituals' own tasks.py`_ uses this to add some local tasks.

Another strategy is to add them in bulk,
so when you write a new task you cannot forget to make it visible:

.. code:: py

    # Register local tasks in root namespace
    from invoke import Task
    for _task in globals().values():
        if isinstance(_task, Task) and _task.body.__module__ == __name__:
            namespace.add_task(_task)

Add the above snippet to the *end* of your ``tasks.py``,
and every *local* task definition gets added to the root namespace.


Constructing Your Own Namespace
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you want to have more control, you can exclude the ``namespace``
identifier from the import and instead define your own.
This example taken from the
`tasks.py of py-generic-project <https://github.com/Springerle/py-generic-project/blob/master/tasks.py>`_
shows how it's done:

.. code:: py

    from rituals.easy import task, Collection
    from rituals.acts.documentation import namespace as _docs

    ...

    namespace = Collection.from_module(sys.modules[__name__], name='')
    namespace.add_collection(_docs)

Note that the ``name=''`` makes this a root namespace.
If you need to be even more selective, import individual tasks from modules
in :py:mod:`rituals.acts` and add them to your namespaces.


.. _`Rituals' own tasks.py`: https://github.com/jhermann/rituals/blob/master/tasks.py#L3


-----------------------------------------------------------------------------
How-Tos
-----------------------------------------------------------------------------

Change default project layout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, sources are expected in ``src/‹packagename›`` and tests in
``src/tests``. However, if you import ``rituals.easy``, an auto-detection
for other layouts (described below) is performed, and only if that fails
for some reason, you need to set the layout type explicitly.

You can change the layout by calling one of the following functions, directly
after the import from ``rituals.invoke_tasks``.

  * ``config.set_maven_layout()`` – Changes locations to
    ``src/main/python/‹packagename›`` and ``src/test/python``.
  * ``config.set_flat_layout()`` – Changes locations to ``‹packagename›``
    and ``tests``.


Change default project configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to override the configuration defaults of various tasks,
without using environment variables, add an ``invoke.yaml`` file in
the same directory where your ``tasks.py`` is located
– usually the project root directory.

This example makes *Sphinx* (as called by the default ``docs`` task)
place generated files in the top-level ``build`` directory instead
of a sub-directory in ``docs``.

.. literalinclude:: ../invoke.yaml
   :caption: invoke.yaml
   :language: yaml
   :emphasize-lines: 3

See :doc:`customize` for a list of possible options.
