.. _winbotsetup:

Detailed winbot configuration description
=========================================

Windows basics
--------------

  * kill unneeded services

    * ALG
    * Automatic Updates (yes!)
    * Computer Browser
    * DHCP Client
    * Print Spooler
    * Remote Registry
    * Server
    * TCP/IP NetBIOS Helper
    * Wireless Configuration

  * Windows firewall

    * kill file and printer sharing on all interfaces
    * allow only RDP, http, https

  * time sync

  * windows update (manual)

    * we should have only security updates, no fancy IE8 etc
    * better dont touch HW (this is VM)
    * restart, repeat windows update
    * kill off all c:\windows\$NtUninstall*, $hf_mig too

  * automatic windows update is OFF! (I hate when it f..s up the system)

  * download: (all downloaded stuff goes into c:\install)

    * firefox
    * freecommander (my personally preferred stuff)
    * programmers notepad (my personal preferred stuff)
    * mydefrag
    * collabnet svn client
    * pythons 2.4 ... 2.6
    * pywin32
    * setuptools
    * mingw32
    * MS Visual C++ 2008 Express Edition
      http://www.microsoft.com/express/downloads/

pythons + pywin32 + setuptools
------------------------------

  * c:\python24_32 NOT default
  * c:\python25_32 NOT default

    * the trick is to install python25_sys+pywin32+setuptools first
      then copy c:\python25_sys to python25_32

  * c:\python26_32 NOT default
  * c:\python26_64 NOT default

    * setuptools trick:
      get the source tgz, patch it with
      http://bugs.python.org/setuptools/issue2

  * c:\python27_32 NOT default
  * c:\python27_64 NOT default

    * setuptools trick: install setuptools from the patched source
      with setup.py install

  * c:\python25_sys (default, 32bit, add to path)
  * install mingw32 to C:\MinGW
  * collabnet svn client to C:\svn
  * MSVC

    * check that build_ext works only with --compiler:
        * mingw32 fails because it's not on path
        * MSVC fails because ENV vars are missing

    * x64 sucks, but use this link:
        * http://www.mathworks.com/support/solutions/en/data/1-6IJJ3L/index.html?solution=1-6IJJ3L

  * create the ``buildbot`` user
  * create own user/other devs

    * setup .buildout (c:\Documents and Settings\<username>\.buildout\default.cfg) ::
      (everyone, please SHARE c:\eggs, the disk is small)

    [buildout]
    eggs-directory=c:\eggs

  * create user on PYPI: zope.wineggbuilder

    * grant perm to packages
    * what's up with ZODB3??? ask Jim
    * setup .pypirc

  * setup buildbot

    * http://buildbot.net/trac/wiki/RunningBuildbotOnWindows
    * grant permissions to user buildbot
    * beat it until it works (permissions, etc....)

  * put an apache in front of the whole

Creating eggs
-------------

The whole process is launched in a nightly buildbot task.

The package that creates the eggs is here:
svn://svn.zope.org/repos/main/Sandbox/adamg/zope.wineggbuilder

This package will build missing binary eggs for specified platforms and package
versions.

A overview how it works::

  * It gets all the released versions from pypi with an xmlrpc query
    (with the method package_releases).

  * Optionally filters the versions (See the specs for
    version/platform constraints)

  * Checks if there are binary eggs present for the various versions/platforms.

  * If one is missing, builds it and uploads to pypi (setup.py bdist_egg),
    taking the source from the svn tag.

If you need a package to be processed contact::

  * Adam Groszer (agroszer-at-gmail-dot-com or)

  * Hanno Schlichting (hannosch-at-hannosch-dot-eu)


Buildbot for tests
------------------

  * Create a file called 'distutils.cfg' in "C:\Python24_32\Lib\distutils".

    [build]
    compiler=mingw32

  * Create a file called 'distutils.cfg' in "C:\Python25_32\Lib\distutils".

    [build]
    compiler=mingw32

  * Create a file called 'setupcompilerandexecute.bat' in "C:\Python24_32".

    set PATH=%PATH%;c:\mingw\bin
    %*

  * Create a file called 'setupcompilerandexecute.bat' in "C:\Python25_32".

    set PATH=%PATH%;c:\mingw\bin
    %*

  * Create a file called 'setupcompilerandexecute.bat' in "C:\Python26_32",
  "C:\Python26_64", "C:\Python27_32", "C:\Python27_64".

    call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\VCVARSALL.bat" x86
    set PATH=%PATH%;"C:\Program Files\Microsoft SDKs\Windows\v6.1\Bin"
    %*

  * for the rest see master.cfg