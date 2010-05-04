=====================================
Automated test suite / nightly builds
=====================================

The ZTK builds on the automated test suites (unit and functional tests) from
the individual projects it keeps track of. We use automated build systems,
like buildbot, to run various combinations of differing Python versions,
operating systems and packages and ensure everything works as expected.


The automated test suite
========================

The ZTK's automated test suite builds on the individual packages' unit and
functional tests and creates a combined test runner that runs each packages'
test suite in isolation but ensures that the dependencies are satisfied using
the ZTK versions under test.

The combined test runner is created using `z3c.recipe.compattest
<http://pypi.python.org/pypi/z3c.recipe.compattest>`_ -- check the
documentation for details.

If you take a ZTK checkout, you can run the tests yourself like this::

    $ svn co svn://svn.zope.org/repos/main/ztk/trunk
    $ python bootstrap.py
    $ bin/buildout
    $ bin/test-ztk

If you work on a ZTK package and want to ensure that your changes are
compatible with a specific version of the ZTK (but using the version of the
package you're working on instead of the version listed in the ZTK) then you
can create a combined test runner in your buildout like this::

    [buildout]
    parts = compattest
    extends = path-to-specific-ztk-version.cfg
    develop = .

    [versions]
    <package-you-work-on> =

    [compattest]
    recipe = z3c.recipe.compattest
    include = ${ztk:packages}


The nightly builds
==================

Build servers
-------------

This is a list of servers that run regular builds of various parts of the code
base.

.. list-table::

    * - **Buildbot**
      - **Contact**
      - **Platforms**
      - **Python**
      - **Packages / Branches**

    * - `The Health Agency <http://dev.thehealthagency.com/buildbot/>`_
      - Jan-Jaap Driessen
      - OS X, Ubuntu 32/64, Windows 
      - 2.4, 2.5, 2.6
      - ZTK, Zope 2, zc.buildout, many grok packages

    * - `POV <http://zope3.pov.lt/buildbot/>`_
      - Marius Gedminas
      - Linux 32/64
      - 2.4, 2.5
      - KGS for Zope 3.4

    * - `AFPY <http://buildbot.afpy.org/>`_
      - Christophe Combelles
      - Linux 32
      - 2.4, 2.5, 2.6, 2.7, 3.1
      - ZTK (trunks and releases), BlueBream template

    * - Securactive `Zope <http://zope.buildbot.securactive.org/>`_
                    `grok <http://grok.buildbot.securactive.org/>`_
                    `bfg <http://bfg.buildbot.securactive.org/>`_
                    `misc <http://misc.buildbot.securactive.org/>`_
      - Sebastien Douche
      - Linux 32/64
      - 2.4, 2.5, 2.6
      - KGS (3.4/3.5), ZTK, grok, BFG (trunk), zc.buildout


Informing the Zope developer community about build results
----------------------------------------------------------

To ensure a reasonable amount of communication from automated systems that
reaches the Zope developers and keeps them aware of the overall build status
we prefer not to send individual build information directly to the
zope-dev@zope.org mailing list.

A separate list (zope-tests@zope.org) exists which you can send build
notifications to.  This list is usually not read by humans. However, a script
aggregates the messages once per day and reports the overall build status back
to zope-dev.

To ensure that your build output is correctly picked up, you need to

- ensure the formatting of the subject line to start with OK/FAILED/UNKNOWN,
- provide a sender email address / sender name that allows to identify the
  build server quickly, and
- subscribe your sender email address to `zope-tests@zope.org
  <https://mail.zope.org/mailman/listinfo/zope-tests>`_

The subject line should be formatted like this::

    <STATUS>: <SUBJECT OF TEST>

    OK: Zope 2.12 on Linux 64-bit with Python 2.4
    FAILED: Zope 2.6 on Windows XP 32-bit with Python 2.5
    UNKNOWN: zope.interface on Linux 64-bit


Automated/nightly build effort coordination
===========================================

Patrik Gerken (do3cc) is the voluntary coordinator for automated builds and
nightly tests.

The responsibility of the coordinator is to help the community reach our goals
regarding:

* achieving and maintaining availability and visibility of automated builds
  and nightly tests

* ensuring coverage of builds/tests with respect to varying Python versions,
  platforms for individual packages, frameworks and toolkits

The coordinator's tasks include:

* Assisting people who want to contribute build machines
* Assisting Zope developers who are missing builds or tests for packages they
  develop
