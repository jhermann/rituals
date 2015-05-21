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

**TODO**


Building Sphinx Documentation
-----------------------------

*Rituals* provides automatic process management of a ``sphinx-autobuild``
daemon, which means you easily get a live-reload preview in your browser.
To start the build watchdog, use ``inv docs -w -b``
– the ``-b`` means to open a new browser tab,
after the server process is ready.
To kill the server, call the ``inv docs -k`` command.
