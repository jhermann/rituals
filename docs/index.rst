..  documentation master file

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

Welcome to the “Rituals” manual!
================================

Overview
--------

“Rituals” is a task library for `Invoke <http://www.pyinvoke.org/>`_
that keeps the most common tasks you always need out of your project,
and makes them centrally maintained. This leaves your ``tasks.py`` small
and to the point, with only things specific to the project at hand. The
following lists the common task implementations that the
``rituals.easy`` module offers. See the next section on how to integrate
them into your ``tasks.py``.

  * ``help`` – Default task, when invoked with no task names.
  * ``clean`` – Perform house-cleaning.
  * ``build`` – Build the project.
  * ``test`` – Perform standard unittests.
  * ``check`` – Perform source code checks.
  * ``release.bump`` – Bump a development version.
  * ``release.dist`` – Distribute the project.
  * ``release.prep`` – Prepare for a release (perform QA checks, and switch to non-dev versioning).
  * … and *many* more, see ``inv -l`` for a complete list.

The guiding principle for these tasks is to strictly separate low-level
tasks for building and installing (via ``setup.py``) from high-level
convenience tasks a developer uses (via ``invoke``). Invoke tasks can
use Setuptools ones as building blocks, but never the other way 'round –
this avoids any bootstrapping headaches during package installations.

Use ``inv -h ‹task›`` as usual to get details on the options of these
tasks. Look at the modules in
`acts <https://github.com/jhermann/rituals/blob/master/src/rituals/acts>`__
if you want to know what these tasks do exactly.

.. note::

    The easiest way to get a working project using ``rituals`` is the
    `py-generic-project <https://github.com/Springerle/py-generic-project>`__
    cookiecutter archetype. That way you have a working project skeleton
    within minutes that is fully equipped, with all aspects of building,
    testing, quality checks, continuous integration, documentation, and
    releasing covered.


Documentation Contents
----------------------

.. toctree::
    :maxdepth: 4

    usage
    tasks
    customize
    api-reference
    CONTRIBUTING
    copyright


References
----------

Tools
^^^^^

  * `Cookiecutter <http://cookiecutter.readthedocs.org/en/latest/>`_
  * `PyInvoke <http://www.pyinvoke.org/>`_
  * `pytest <http://pytest.org/latest/contents.html>`_
  * `tox <https://tox.readthedocs.org/en/latest/>`_
  * `Pylint <http://docs.pylint.org/>`_
  * `twine <https://github.com/pypa/twine#twine>`_
  * `bpython <http://docs.bpython-interpreter.org/>`_
  * `yolk3k <https://github.com/myint/yolk#yolk>`_


Indices and Tables
------------------

  * :ref:`genindex`
  * :ref:`modindex`
  * :ref:`search`
