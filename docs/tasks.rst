..  documentation: tasks

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

Tasks Reference
===============


Fundamental Tasks
-----------------

**TODO**


Documentation Tasks
-------------------

Building Sphinx Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Rituals* provides automatic process management of a ``sphinx-autobuild``
daemon, which means you easily get a live-reload preview in your browser.
To start the build watchdog, use ``inv docs -w -b``.
The ``-b`` means to open a new browser tab,
after the server process is ready.
To kill the server, call the ``inv docs -k`` command.
You can check on the status of a running daemon with ``inv docs -s``.

Note that sometimes you have to manually trigger a full rebuild via
``inv docs --clean``, especially when you make structural changes
(e.g. adding new chapters to the main toc-tree).
Your browser will change the view to an empty canvas, just
initiate a reload (``Ctrl-R``) when the build is done.
Typically this is needed when the sidebar TOC is out of sync, which happens
due to the optimizations in ``sphinx-autobuild`` that make it so responsive.



Release Workflow
----------------

Preparing a Release
^^^^^^^^^^^^^^^^^^^

**TODO**


Building a PEX Distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**TODO**
