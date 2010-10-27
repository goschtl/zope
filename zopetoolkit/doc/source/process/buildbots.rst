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

    $ svn co svn://svn.zope.org/repos/main/zopetoolkit/trunk
    $ python bootstrap.py
    $ bin/buildout
    $ bin/test-ztk && bin/test-zopeapp

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

MAC OS X
~~~~~~~~

The software currently being tested is not compatible with python 2.4.
The tests run on OS X 10.6

.. list-table::

    * - **Project**
      - **OS X / Python2.4**
      - **OS X / Python2.5**
      - **OS X / Python2.6**
      - **OS X / Python2.7**

    * - `Zope 2.12 <http://svn.zope.org/Zope/branches/2.12>`__
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.12-py2.6%20slave-osx THA
      - unsupported

    * - `Zope 2.13 <http://svn.zope.org/Zope/branches/2.13>`__
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.13-py2.6%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.13-py2.7%20slave-osx THA

    * - `Zope 2 trunk <http://svn.zope.org/Zope/trunk>`__
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.14-py2.6%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.14-py2.7%20slave-osx THA

    * - `ZTK 1.0 <http://svn.zope.org/zopetoolkit/branches/1.0>`__
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.4%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.5%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.6%20slave-osx THA
      - unsupported

    * - `ZTK trunk <http://svn.zope.org/zopetoolkit/trunk>`__
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.5%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.6%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.7%20slave-osx THA

    * - `Groktoolkit 1.2 <http://svn.zope.org/groktoolkit/branches/1.2>`__
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-1.2-py2.5%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-1.2-py2.6%20slave-osx THA
      - unsupported

    * - `Groktoolkit trunk <http://svn.zope.org/groktoolkit/trunk>`__
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.5%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.6%20slave-osx THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.7%20slave-osx THA

Windows
~~~~~~~

The winbot is configured to compile C-Extensions, while the ztk
environment isn't.
A rumour is that pythons before 2.6 are unstable on Win64, therefore
no testing support for those

.. list-table::

    * - **Project**
      - **Win32 / Py2.4**
      - **Win32 / Py2.5**
      - **Win32 / Py2.6**
      - **Win32 / Py2.7**
      - **Win64 / Py2.6**
      - **Win64 / Py2.7**

    * - `Zope 2.13 <http://svn.zope.org/Zope/branches/2.13>`__
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.13_win-py2.6%20slave-win THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.13_win-py2.7%20slave-win THA
      - unsupported
      - unsupported

    * - `ZODB trunk <http://svn.zope.org/ZODB/trunk>`__
      - unsupported
      - .. buildbotresult:: http://winbot.zope.org/builders/ZODB_dev%20py_254_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/ZODB_dev%20py_265_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/ZODB_dev%20py_270_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/ZODB_dev%20py_265_win64 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/ZODB_dev%20py_270_win64 winbot

    * - `ZTK 1.0 <http://svn.zope.org/zopetoolkit/branches/1.0>`__
      - .. buildbotresult:: http://winbot.zope.org/builders/ztk_10%20py_244_win32 winbot
      - * .. buildbotresult:: http://winbot.zope.org/builders/ztk_10%20py_254_win32 winbot
        * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0_win-py2.5%20slave-win THA
      - * .. buildbotresult:: http://winbot.zope.org/builders/ztk_10%20py_265_win32 winbot
        * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0_win-py2.6%20slave-win THA
      - unsupported
      - .. buildbotresult:: http://winbot.zope.org/builders/ztk_10%20py_265_win64 winbot
      - unsupported

    * - `ZTK trunk <http://svn.zope.org/zopetoolkit/trunk>`__
      - unsupported
      - * .. buildbotresult:: http://winbot.zope.org/builders/ztk_dev%20py_254_win32 winbot
        * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit_win-py2.5%20slave-win THA
      - * .. buildbotresult:: http://winbot.zope.org/builders/ztk_dev%20py_265_win32 winbot
        * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit_win-py2.6%20slave-win THA
      - * .. buildbotresult:: http://winbot.zope.org/builders/ztk_dev%20py_270_win32 winbot
        * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit_win-py2.7%20slave-win THA
      - .. buildbotresult:: http://winbot.zope.org/builders/ztk_dev%20py_265_win64 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/ztk_dev%20py_270_win64 winbot

    * - `zc.buildout trunk <http://svn.zope.org/zc.buildout/trunk>`__
      - unsupported
      - .. buildbotresult:: http://winbot.zope.org/builders/zc_buildout_dev%20py_254_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/zc_buildout_dev%20py_265_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/zc_buildout_dev%20py_270_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/zc_buildout_dev%20py_265_win64 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/zc_buildout_dev%20py_270_win64 winbot

    * - `Bluebream <http://svn.zope.org/bluebream/trunk>`__
      - .. buildbotresult:: http://winbot.zope.org/builders/BlueBream_dev%20py_244_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/BlueBream_dev%20py_254_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/BlueBream_dev%20py_265_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/BlueBream_dev%20py_270_win32 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/BlueBream_dev%20py_265_win64 winbot
      - .. buildbotresult:: http://winbot.zope.org/builders/BlueBream_dev%20py_270_win64 winbot

    * - `Groktoolkit 1.2 <http://svn.zope.org/groktoolkit/branches/1.2>`__
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-1.2_win-py2.5%20slave-win THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-1.2_win-py2.6%20slave-win THA
      - unsupported
      - unsupported
      - unsupported

    * - `Groktoolkit trunk <http://svn.zope.org/groktoolkit/trunk>`__
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit_win-py2.5%20slave-win THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit_win-py2.6%20slave-win THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit_win-py2.7%20slave-win THA
      - unsupported
      - unsupported

Linux
~~~~~

.. list-table::

    * - **Project**
      - **Linux32 / Py2.4**
      - **Linux32 / Py2.5**
      - **Linux32 / Py2.6**
      - **Linux32 / Py2.7**
      - **Linux64 / Py2.4**
      - **Linux64 / Py2.5**
      - **Linux64 / Py2.6**
      - **Linux64 / Py2.7**

    * - `Zope 2.10 <http://svn.zope.org/Zope/branches/2.10>`__
      -
      - unsupported
      - unsupported
      - unsupported
      - EPY
      - unsupported
      - unsupported
      - unsupported

    * - `Zope 2.11 <http://svn.zope.org/Zope/branches/2.11>`__
      -
      - unsupported
      - unsupported
      - unsupported
      - EPY
      - unsupported
      - unsupported
      - unsupported

    * - `Zope 2.12 <http://svn.zope.org/Zope/branches/2.12>`__
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.12-py2.6%20slave-ubuntu32 THA
      - unsupported
      - unsupported
      - unsupported
      - * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.12-py2.6%20slave-ubuntu64 THA
        * EPY
      - unsupported

    * - `Zope 2.13 <http://svn.zope.org/Zope/branches/2.13>`__
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.13-py2.6%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.13-py2.7%20slave-ubuntu32 THA
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.13-py2.6%20slave-ubuntu64 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.13-py2.7%20slave-ubuntu64 THA

    * - `Zope 2.14 (trunk) <http://svn.zope.org/Zope/trunk>`__
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.14-py2.6%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.14-py2.7%20slave-ubuntu32 THA
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.14-py2.6%20slave-ubuntu64 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zope2.14-py2.7%20slave-ubuntu64 THA

    * - `Zope 3.4 KGS <http://svn.zope.org/zope.release/branches/3.4>`__
      - .. buildbotresult:: http://zope3.pov.lt/buildbot/builders/py2.4-32bit-linux POV
      - .. buildbotresult:: http://zope3.pov.lt/buildbot/builders/py2.5-32bit-linux POV
      - unsupported
      - unsupported
      - * .. buildbotresult:: http://buildbot.afpy.org/kgs3.4/builders/Python2.4.6%2064bit%20linux AFPY
        * .. buildbotresult:: http://zope3.pov.lt/buildbot/builders/py2.4-64bit-linux POV
      - * .. buildbotresult:: http://buildbot.afpy.org/kgs3.4/builders/Python2.5.5%2064bit%20linux AFPY
        * .. buildbotresult:: http://zope3.pov.lt/buildbot/builders/py2.5-64bit-linux POV
      - unsupported
      - unsupported

    * - `ZTK 1.0 <http://svn.zope.org/zopetoolkit/branches/1.0>`__
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.4%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.5%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.6%20slave-ubuntu32 THA
      - unsupported
      - * .. buildbotresult:: http://buildbot.afpy.org/ztk1.0/builders/Python2.4.6%20Linux%2064bit AFPY
        * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.4%20slave-ubuntu64 THA
      - * .. buildbotresult:: http://buildbot.afpy.org/ztk1.0/builders/Python2.5.5%20Linux%2064bit AFPY
        * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.5%20slave-ubuntu64 THA
      - * .. buildbotresult:: http://buildbot.afpy.org/ztk1.0/builders/Python2.6.5%20Linux%2064bit AFPY
        * .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-1.0-py2.6%20slave-ubuntu64 THA
      - unsupported

    * - `ZTK 1.0 <http://svn.zope.org/zopetoolkit/branches/1.0>`_ dev
      -
      -
      -
      - unsupported
      - .. buildbotresult:: http://buildbot.afpy.org/ztk1.0dev/builders/Python2.4.6%20Linux%2064bit AFPY
      - .. buildbotresult:: http://buildbot.afpy.org/ztk1.0dev/builders/Python2.5.5%20Linux%2064bit AFPY
      - .. buildbotresult:: http://buildbot.afpy.org/ztk1.0dev/builders/Python2.6.5%20Linux%2064bit AFPY
      - unsupported

    * - `ZTK trunk <http://svn.zope.org/zopetoolkit/trunk>`_
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.5%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.6%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.7%20slave-ubuntu32 THA
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.5%20slave-ubuntu64 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.6%20slave-ubuntu64 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/zopetoolkit-py2.7%20slave-ubuntu64 THA

    * - `Bluebream <http://svn.zope.org/bluebream/trunk>`__
      -
      -
      -
      -
      - .. buildbotresult:: http://buildbot.afpy.org/bluebream/builders/Python2.4.6%2064bit%20linux AFPY
      - .. buildbotresult:: http://buildbot.afpy.org/bluebream/builders/Python2.5.5%2064bit%20linux AFPY
      - .. buildbotresult:: http://buildbot.afpy.org/bluebream/builders/Python2.6.5%2064bit%20linux AFPY
      - .. buildbotresult:: http://buildbot.afpy.org/bluebream/builders/Python2.7.0%2064bit%20linux AFPY

    * - `Groktoolkit 1.2 <http://svn.zope.org/groktoolkit/branches/1.2>`__
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-1.2-py2.5%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-1.2-py2.6%20slave-ubuntu32 THA
      - unsupported
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-1.2-py2.5%20slave-ubuntu64 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-1.2-py2.6%20slave-ubuntu64 THA
      - unsupported

    * - `Groktoolkit trunk <http://svn.zope.org/groktoolkit/trunk>`__
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.5%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.6%20slave-ubuntu32 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.7%20slave-ubuntu32 THA
      - unsupported
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.5%20slave-ubuntu64 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.6%20slave-ubuntu64 THA
      - .. buildbotresult:: http://dev.thehealthagency.com/buildbot/builders/groktoolkit-py2.7%20slave-ubuntu64 THA


The Buildbot Maintainers
~~~~~~~~~~~~~~~~~~~~~~~~

We would like to thank all providers of automated test facilities:

.. list-table::

    * - **Buildbot**
      - **Contact**
      - **Platforms**
      - **Python**
      - **Packages / Branches**

    * - `The Health Agency <http://dev.thehealthagency.com/buildbot/>`_ (THA)
      - Jan-Jaap Driessen
      - OS X, Ubuntu 32/64, Windows
      - 2.4, 2.5, 2.6, 2.7
      - ZTK, Zope 2, groktoolkit, many grok and ZTK packages

    * - `POV <http://zope3.pov.lt/buildbot/>`_
      - Marius Gedminas
          IRC: mgedmin
      - Linux 32/64
      - 2.4, 2.5, 2.6, 2.7, 3.1
      - KGS for Zope 3.4

    * - `AFPY <http://buildbot.afpy.org/>`_
      - Christophe Combelles
      - Linux 64
      - 2.4, 2.5, 2.6, 2.7, 3.1
      - ZTK 1.0 (trunks and releases), BlueBream template

    * - Securactive
                    `Zope <http://zope.buildbot.securactive.org/>`_
                    `grok <http://grok.buildbot.securactive.org/>`_
                    `bfg <http://bfg.buildbot.securactive.org/>`_
                    `misc <http://misc.buildbot.securactive.org/>`_
      - Sebastien Douche
      - Linux 32/64
      - 2.4, 2.5, 2.6
      - KGS (3.4/3.5), ZTK, grok, BFG (trunk), zc.buildout

    * - EPY
      - Stefan Holek
      - Linux 64
      - 2.6
      - Zope 2, CMF, Plone

    * - `winbot <http://winbot.zope.org/>`_ (project sponsored by the Zope foundation)
      - Adam Groszer
      - Windows 32 and 64 bits
      - 2.4, 2.5, 2.6, 2.7
      - ZTK (trunks and releases), BlueBream template, ZODB,


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
- you can bug Jens to add the address if you can't receive mails with it

The subject line should be formatted like this::

    <STATUS>: <SUBJECT OF TEST>

    OK: Zope 2.12 on Linux 64-bit with Python 2.4
    FAILED: Zope 2.6 on Windows XP 32-bit with Python 2.5
    UNKNOWN: zope.interface on Linux 64-bit

Here is a sample message_formatter function for the buildbot ``MailNotifier`` ::

    def message_formatter(mode, name, build, results, master_status):
        """Provide a customized message to BuildBot's MailNotifier."""
        result = Results[results]

        text = list()

        # status required by zope-tests list
        # http://docs.zope.org/zopetoolkit/process/buildbots.html
        status = 'UNKNOWN'
        if result == 'success':
            status = 'OK'
        if result == 'failure':
            status = 'FAILED'

        subject = '%s : %s / %s' % (status, master_status.getProjectName(), name)
        text.append(subject)
        text.append("Build: %s" % master_status.getURLForThing(build))
        text.append('\n')
        text.append("Build Reason: %s" % build.getReason())
        text.append('\n')

        source = ""
        ss = build.getSourceStamp()
        if ss.branch:
            source += "[branch %s] " % ss.branch
        if ss.revision:
            source += ss.revision
        else:
            source += "HEAD"
        if ss.patch:
            source += " (plus patch)"
        text.append("Build Source Stamp: %s" % source)
        text.append('\n')
        text.append("Blamelist: %s" % ", ".join(build.getResponsibleUsers()))
        text.append('\n')
        text.append("Buildbot: %s" % master_status.getBuildbotURL())
        return {
            'body': "\n".join(text),
            'type': 'plain',
            'subject': subject,
            }

Some links to sample configs:

* http://buildbot.afpy.org/ztk1.0/master.cfg
* http://buildbot.afpy.org/ztk1.0dev/master.cfg
* http://buildbot.afpy.org/bluebream/master.cfg
* http://svn.zope.org/repos/main/zope.wineggbuilder/trunk/master.cfg
* http://zope3.pov.lt/master.cfg
* http://svn.zope.org/repos/main/Sandbox/janjaapdriessen/buildbot/buildout.cfg

See also :ref:`winbotdetails`


Automated/nightly build effort coordination
===========================================

Patrick Gerken (do3cc) is the voluntary coordinator for automated builds and
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
