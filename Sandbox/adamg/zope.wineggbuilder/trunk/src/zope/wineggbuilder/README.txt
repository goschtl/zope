Building windows binary eggs
----------------------------

Install mocks:

    >>> from zope.wineggbuilder import base
    >>> from zope.wineggbuilder import build
    >>> from zope.wineggbuilder import testing

    >>> oldSVNcommand = base.SVN.commandKlass
    >>> base.SVN.commandKlass = testing.MockCommand()

    >>> oldCompilerCommand = build.Compiler.commandKlass
    >>> build.Compiler.commandKlass = testing.MockCommand()

    >>> oldPYPI = build.Package.pypiKlass
    >>> build.Package.pypiKlass = testing.MockPYPI()

    >>> oldURLgetter = build.Package.urlGetterKlass
    >>> build.Package.urlGetterKlass = testing.MockURLGetter()

Let's see:

    >>> import os.path
    >>> testininame = os.path.join(os.path.dirname(build.__file__), 'test.ini')
    >>> build.main([testininame, '-v']) # doctest: +REPORT_NDIFF
    INFO - loading configuration from /home/adi/zopefix/zope.wineggbuilder/trunk/src/zope/wineggbuilder/test.ini
    INFO - Starting to build
    DEBUG - getting http://pypi.python.org/simple/zope.proxy/
    DEBUG - Got a file: zope.proxy-3.4.0-py2.4-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.0.tar.gz
    DEBUG - Got a file: zope.proxy-3.4.2.zip
    DEBUG - Got a file: zope.proxy-3.4.2-py2.6-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.1-py2.4-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.1.zip
    DEBUG - Got a file: zope.proxy-3.4.2-py2.5-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.2-py2.4-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.0-py2.5-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.0.zip
    DEBUG - Checking if build required for zope.proxy 3.4.0 py25_32
    DEBUG - Build not required for zope.proxy 3.4.0 py25_32
    DEBUG - Checking if build required for zope.proxy 3.4.0 py26_32
    DEBUG - Build required for zope.proxy 3.4.0 py26_32
    DEBUG - Command: svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.0 /tmp/tmp...wineggbuilder
    DEBUG - Output:
    A    /tmp/tmpgqt2dHwineggbuilder/bootstrap.py
    A    /tmp/tmpgqt2dHwineggbuilder/buildout.cfg
    A    /tmp/tmpgqt2dHwineggbuilder/CHANGES.txt
    A    /tmp/tmpgqt2dHwineggbuilder/setup.py
    A    /tmp/tmpgqt2dHwineggbuilder/src
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/_zope_proxy_proxy.c
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/tests
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/tests/__init__.py
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/tests/test_proxy.py
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/tests/test_decorator.py
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/__init__.py
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/proxy.h
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/decorator.py
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/proxy/interfaces.py
    A    /tmp/tmpgqt2dHwineggbuilder/src/zope/__init__.py
    A    /tmp/tmpgqt2dHwineggbuilder/README.txt
     U   /tmp/tmpgqt2dHwineggbuilder
    Checked out revision 113298.
    INFO - Starting build for zope.proxy 3.4.0 py26_32
    DEBUG - Running: call c:\program files\msvc\msvcvars.bat
    c:\Python26\python setup.py build_ext --compiler msvc bdist_egg upload
    In: /tmp/tmp...wineggbuilder
    DEBUG - Command: /tmp/tmp...bat
    DEBUG - Output:
    <BLANKLINE>
    <BLANKLINE>
    DEBUG - Checking if build required for zope.proxy 3.4.1 py25_32
    DEBUG - Build required for zope.proxy 3.4.1 py25_32
    DEBUG - Checking if build required for zope.proxy 3.4.1 py26_32
    DEBUG - Build required for zope.proxy 3.4.1 py26_32
    DEBUG - Command: svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.1 /tmp/tmp...wineggbuilder
    DEBUG - Output:
    A    /tmp/tmpKNdQxlwineggbuilder/bootstrap.py
    A    /tmp/tmpKNdQxlwineggbuilder/buildout.cfg
    A    /tmp/tmpKNdQxlwineggbuilder/CHANGES.txt
    A    /tmp/tmpKNdQxlwineggbuilder/test.py
    A    /tmp/tmpKNdQxlwineggbuilder/setup.py
    A    /tmp/tmpKNdQxlwineggbuilder/src
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/_zope_proxy_proxy.c
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/tests
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/tests/__init__.py
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/tests/test_proxy.py
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/tests/test_decorator.py
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/DEPENDENCIES.cfg
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/__init__.py
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/proxy.h
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/decorator.py
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/interfaces.py
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/proxy/SETUP.cfg
    A    /tmp/tmpKNdQxlwineggbuilder/src/zope/__init__.py
    A    /tmp/tmpKNdQxlwineggbuilder/README.txt
     U   /tmp/tmpKNdQxlwineggbuilder
    Checked out revision 113298.
    INFO - Starting build for zope.proxy 3.4.1 py25_32
    DEBUG - Running: set PATH=%PATH%;c:\mingw32\bin
    c:\Python25\python setup.py build_ext --compiler mingw32 bdist_egg upload
    In: /tmp/tmp...wineggbuilder
    DEBUG - Command: /tmp/tmp...bat
    DEBUG - Output:
    <BLANKLINE>
    <BLANKLINE>
    INFO - Starting build for zope.proxy 3.4.1 py26_32
    DEBUG - Running: call c:\program files\msvc\msvcvars.bat
    c:\Python26\python setup.py build_ext --compiler msvc bdist_egg upload
    In: /tmp/tmp...wineggbuilder
    DEBUG - Command: /tmp/tmp...bat
    DEBUG - Output:
    <BLANKLINE>
    <BLANKLINE>
    DEBUG - Checking if build required for zope.proxy 3.4.2 py25_32
    DEBUG - Build not required for zope.proxy 3.4.2 py25_32
    DEBUG - Checking if build required for zope.proxy 3.4.2 py26_32
    DEBUG - Build not required for zope.proxy 3.4.2 py26_32
    INFO - Done.

Let's see what was executed on mocks:

    >>> from pprint import pprint
    >>> pprint(testing.MOCKLOG)
    ['package_releases: zope.proxy',
     'urlget: http://pypi.python.org/simple/zope.proxy/',
     'cmd: svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.0 /tmp/tmp...wineggbuilder in None',
     'cmd: /tmp/tmp...bat in /tmp/tmp...wineggbuilder',
     'cmd: svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.1 /tmp/tmp...wineggbuilder in None',
     'cmd: /tmp/tmp...bat in /tmp/tmp...wineggbuilder',
     'cmd: /tmp/tmp...bat in /tmp/tmp...wineggbuilder']

Remove mocks:

    >>> base.SVN.commandKlass = oldSVNcommand
    >>> build.Compiler.commandKlass = oldCompilerCommand
    >>> build.Package.pypiKlass = oldPYPI
    >>> build.Package.urlGetterKlass = oldURLgetter
