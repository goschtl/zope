==========================
Automated builds and tests
==========================

List of servers
===============

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
      - Sebastian Douche
      - Linux 32/64
      - 2.4, 2.5, 2.6
      - KGS (3.4/3.5), ZTK, grok, BFG (trunk), zc.buildout


Notifications
=============

To ensure a reasonable amount of communication from automated systems that
reaches the Zope developers and keeps them aware of the overall build status
we prefer not to send individual build information directly to the
zope-dev@zope.org mailing list.

A separate list (zope-tests@zope.org) exists which you can send build
notifications to.  This list is usually not read by humans. However, a script
aggregates the messages once per day and reports the overall build status back
to zope-dev.

To ensure that your build output is correctly picked up, you need to

- ensure the formatting of the subject line to start with OK/FAILURE/UNKNOWN,
- provide a sender email address / sender name that allows to identify the
  build server quickly, and
- subscribe your sender email address to `zope-tests@zope.org
  <https://mail.zope.org/mailman/listinfo/zope-tests>`_

The subject line should be formatted like this::

    <STATUS>: <SUBJECT OF TEST>

    OK: Zope 2.12 on Linux 64-bit with Python 2.4
    FAILURE: Zope 2.6 on Windows XP 32-bit with Python 2.5
    UNKNOWN: zope.interface on Linux 64-bit
