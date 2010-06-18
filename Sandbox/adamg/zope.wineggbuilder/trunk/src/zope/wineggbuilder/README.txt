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
    >>> build.main([testininame, '-v', '-s']) # doctest: +REPORT_NDIFF
    INFO - loading configuration from ...zope.wineggbuilder\trunk\src\zope\wineggbuilder\test.ini
    INFO - Starting to build
    INFO - Processing zope.proxy [zope.proxy_34_to_35]
    DEBUG - getting http://pypi.python.org/simple/zope.proxy/
    DEBUG - Got a file: zope.proxy-3.5.0-py2.6-win-amd64.egg
    DEBUG - Got a file: zope.proxy-3.5.0-py2.6-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.0-py2.4-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.0.tar.gz
    DEBUG - Got a file: zope.proxy-3.5.0-py2.5-win32.egg
    DEBUG - Got a file: zope.proxy-3.5.0.tar.gz
    DEBUG - Got a file: zope.proxy-3.4.2.zip
    DEBUG - Got a file: zope.proxy-3.5.0-py2.4-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.2-py2.6-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.1-py2.4-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.1.zip
    DEBUG - Got a file: zope.proxy-3.4.2-py2.5-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.2-py2.4-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.0-py2.5-win32.egg
    DEBUG - Got a file: zope.proxy-3.4.0.zip
    DEBUG - Checking if build required for [zope.proxy_34_to_35] zope.proxy 3.4.0 py25_32
    DEBUG - Build not required for [zope.proxy_34_to_35] zope.proxy 3.4.0 py25_32
    DEBUG - Checking if build required for [zope.proxy_34_to_35] zope.proxy 3.4.0 py26_32
    DEBUG - Build required for [zope.proxy_34_to_35] zope.proxy 3.4.0 py26_32
    DEBUG - Command: svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.0 ...wineggbuilder
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
    INFO - Starting build for [zope.proxy_34_to_35] zope.proxy 3.4.0 py26_32
    DEBUG - Running: call c:\program files\msvc\msvcvars.bat
    c:\Python26\python setup.py build_ext --compiler msvc bdist_egg upload
    In: ...wineggbuilder
    DEBUG - Command: ...bat
    DEBUG - Output:
    running bdist_egg
    running egg_info
    creating src\zope.proxy.egg-info
    writing requirements to src\zope.proxy.egg-info\requires.txt
    writing src\zope.proxy.egg-info\PKG-INFO
    writing namespace_packages to src\zope.proxy.egg-info\namespace_packages.txt
    writing top-level names to src\zope.proxy.egg-info\top_level.txt
    writing dependency_links to src\zope.proxy.egg-info\dependency_links.txt
    writing manifest file 'src\zope.proxy.egg-info\SOURCES.txt'
    unrecognized .svn/entries format in
    reading manifest file 'src\zope.proxy.egg-info\SOURCES.txt'
    writing manifest file 'src\zope.proxy.egg-info\SOURCES.txt'
    creating zope.proxy-3.6.1dev
    creating zope.proxy-3.6.1dev\src
    creating zope.proxy-3.6.1dev\src\zope
    creating zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    creating zope.proxy-3.6.1dev\src\zope\proxy
    copying files to zope.proxy-3.6.1dev...
    copying README.txt -> zope.proxy-3.6.1dev
    copying setup.py -> zope.proxy-3.6.1dev
    copying src\zope\__init__.py -> zope.proxy-3.6.1dev\src\zope
    copying src\zope.proxy.egg-info\PKG-INFO -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\SOURCES.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\dependency_links.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\namespace_packages.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\not-zip-safe -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\requires.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\top_level.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope\proxy\__init__.py -> zope.proxy-3.6.1dev\src\zope\proxy
    copying src\zope\proxy\_zope_proxy_proxy.c -> zope.proxy-3.6.1dev\src\zope\proxy
    copying src\zope\proxy\decorator.py -> zope.proxy-3.6.1dev\src\zope\proxy
    copying src\zope\proxy\interfaces.py -> zope.proxy-3.6.1dev\src\zope\proxy
    Writing zope.proxy-3.6.1dev\setup.cfg
    creating dist
    creating 'dist\zope.proxy-3.6.1dev.egg' and adding 'zope.proxy-3.6.1dev' to it
    adding 'zope.proxy-3.6.1dev\PKG-INFO'
    adding 'zope.proxy-3.6.1dev\README.txt'
    adding 'zope.proxy-3.6.1dev\setup.cfg'
    adding 'zope.proxy-3.6.1dev\setup.py'
    adding 'zope.proxy-3.6.1dev\src\zope\__init__.py'
    adding 'zope.proxy-3.6.1dev\src\zope\proxy\decorator.py'
    adding 'zope.proxy-3.6.1dev\src\zope\proxy\interfaces.py'
    adding 'zope.proxy-3.6.1dev\src\zope\proxy\_zope_proxy_proxy.c'
    adding 'zope.proxy-3.6.1dev\src\zope\proxy\__init__.py'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\dependency_links.txt'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\namespace_packages.txt'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\not-zip-safe'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\PKG-INFO'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\requires.txt'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\SOURCES.txt'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\top_level.txt'
    removing 'zope.proxy-3.6.1dev' (and everything under it)
    running upload
    Submitting dist\zope.proxy-3.6.1dev.egg to http://pypi.refline.ch/eggs
    Server response (200): OK
    INFO - Upload seems to be OK.
    running upload
    Submitting dist\zope.proxy-3.6.1dev.egg to http://pypi.refline.ch/eggs
    Server response (200): OK
    DEBUG - Checking if build required for [zope.proxy_34_to_35] zope.proxy 3.4.1 py25_32
    DEBUG - Build required for [zope.proxy_34_to_35] zope.proxy 3.4.1 py25_32
    DEBUG - Checking if build required for [zope.proxy_34_to_35] zope.proxy 3.4.1 py26_32
    DEBUG - Build required for [zope.proxy_34_to_35] zope.proxy 3.4.1 py26_32
    DEBUG - Command: svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.1 ...wineggbuilder
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
    INFO - Starting build for [zope.proxy_34_to_35] zope.proxy 3.4.1 py25_32
    DEBUG - Running: set PATH=%PATH%;c:\mingw32\bin
    c:\Python25\python setup.py build_ext --compiler mingw32 bdist_egg upload
    In: ...wineggbuilder
    DEBUG - Command: ...bat
    DEBUG - Output:
    running bdist_egg
    running egg_info
    creating src\zope.proxy.egg-info
    writing requirements to src\zope.proxy.egg-info\requires.txt
    writing src\zope.proxy.egg-info\PKG-INFO
    writing namespace_packages to src\zope.proxy.egg-info\namespace_packages.txt
    writing top-level names to src\zope.proxy.egg-info\top_level.txt
    writing dependency_links to src\zope.proxy.egg-info\dependency_links.txt
    writing manifest file 'src\zope.proxy.egg-info\SOURCES.txt'
    unrecognized .svn/entries format in
    reading manifest file 'src\zope.proxy.egg-info\SOURCES.txt'
    writing manifest file 'src\zope.proxy.egg-info\SOURCES.txt'
    creating zope.proxy-3.6.1dev
    creating zope.proxy-3.6.1dev\src
    creating zope.proxy-3.6.1dev\src\zope
    creating zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    creating zope.proxy-3.6.1dev\src\zope\proxy
    copying files to zope.proxy-3.6.1dev...
    copying README.txt -> zope.proxy-3.6.1dev
    copying setup.py -> zope.proxy-3.6.1dev
    copying src\zope\__init__.py -> zope.proxy-3.6.1dev\src\zope
    copying src\zope.proxy.egg-info\PKG-INFO -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\SOURCES.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\dependency_links.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\namespace_packages.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\not-zip-safe -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\requires.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope.proxy.egg-info\top_level.txt -> zope.proxy-3.6.1dev\src\zope.proxy.egg-info
    copying src\zope\proxy\__init__.py -> zope.proxy-3.6.1dev\src\zope\proxy
    copying src\zope\proxy\_zope_proxy_proxy.c -> zope.proxy-3.6.1dev\src\zope\proxy
    copying src\zope\proxy\decorator.py -> zope.proxy-3.6.1dev\src\zope\proxy
    copying src\zope\proxy\interfaces.py -> zope.proxy-3.6.1dev\src\zope\proxy
    Writing zope.proxy-3.6.1dev\setup.cfg
    creating dist
    creating 'dist\zope.proxy-3.6.1dev.egg' and adding 'zope.proxy-3.6.1dev' to it
    adding 'zope.proxy-3.6.1dev\PKG-INFO'
    adding 'zope.proxy-3.6.1dev\README.txt'
    adding 'zope.proxy-3.6.1dev\setup.cfg'
    adding 'zope.proxy-3.6.1dev\setup.py'
    adding 'zope.proxy-3.6.1dev\src\zope\__init__.py'
    adding 'zope.proxy-3.6.1dev\src\zope\proxy\decorator.py'
    adding 'zope.proxy-3.6.1dev\src\zope\proxy\interfaces.py'
    adding 'zope.proxy-3.6.1dev\src\zope\proxy\_zope_proxy_proxy.c'
    adding 'zope.proxy-3.6.1dev\src\zope\proxy\__init__.py'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\dependency_links.txt'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\namespace_packages.txt'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\not-zip-safe'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\PKG-INFO'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\requires.txt'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\SOURCES.txt'
    adding 'zope.proxy-3.6.1dev\src\zope.proxy.egg-info\top_level.txt'
    removing 'zope.proxy-3.6.1dev' (and everything under it)
    running upload
    Submitting dist\zope.proxy-3.6.1dev.egg to http://pypi.refline.ch/eggs
    Server response (200): OK
    INFO - Upload seems to be OK.
    running upload
    Submitting dist\zope.proxy-3.6.1dev.egg to http://pypi.refline.ch/eggs
    Server response (200): OK
    INFO - Starting build for [zope.proxy_34_to_35] zope.proxy 3.4.1 py26_32
    DEBUG - Running: call c:\program files\msvc\msvcvars.bat
    c:\Python26\python setup.py build_ext --compiler msvc bdist_egg upload
    In: ...wineggbuilder
    DEBUG - Command: ...bat
    DEBUG - Output:
    running build_ext
    building 'zope.proxy._zope_proxy_proxy' extension
    writing build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.def
    C:\MingW\bin\gcc.exe -mno-cygwin -shared -s build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.def -LU:\Python25\libs -LU:\Python25\PCbuild -lpython25 -lmsvcr71 -o build\lib.win32-2.5\zope\proxy\_zope_proxy_proxy.pyd
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x60): undefined reference to `_imp__PyExc_TypeError'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x106): undefined reference to `_imp__PyExc_TypeError'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x26e): undefined reference to `_imp__PyTuple_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x275): undefined reference to `_imp__PyTuple_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x2d2): undefined reference to `_imp__PyClass_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x2e2): undefined reference to `_imp__PyType_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x2e9): undefined reference to `_imp__PyType_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x32c): undefined reference to `_imp__PyDict_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x333): undefined reference to `_imp__PyDict_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x3a8): undefined reference to `_imp__PyUnicode_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x3af): undefined reference to `_imp__PyUnicode_Type'
    collect2: ld returned 1 exit status
    error: command 'gcc' failed with exit status 1
    INFO - Something was wrong with the command. Output: running build_ext
    building 'zope.proxy._zope_proxy_proxy' extension
    writing build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.def
    C:\MingW\bin\gcc.exe -mno-cygwin -shared -s build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.def -LU:\Python25\libs -LU:\Python25\PCbuild -lpython25 -lmsvcr71 -o build\lib.win32-2.5\zope\proxy\_zope_proxy_proxy.pyd
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x60): undefined reference to `_imp__PyExc_TypeError'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x106): undefined reference to `_imp__PyExc_TypeError'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x26e): undefined reference to `_imp__PyTuple_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x275): undefined reference to `_imp__PyTuple_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x2d2): undefined reference to `_imp__PyClass_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x2e2): undefined reference to `_imp__PyType_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x2e9): undefined reference to `_imp__PyType_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x32c): undefined reference to `_imp__PyDict_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x333): undefined reference to `_imp__PyDict_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x3a8): undefined reference to `_imp__PyUnicode_Type'
    build\temp.win32-2.5\Release\src\zope\proxy\_zope_proxy_proxy.o:_zope_proxy_proxy.c:(.text+0x3af): undefined reference to `_imp__PyUnicode_Type'
    collect2: ld returned 1 exit status
    error: command 'gcc' failed with exit status 1
    DEBUG - Checking if build required for [zope.proxy_34_to_35] zope.proxy 3.4.2 py25_32
    DEBUG - Build not required for [zope.proxy_34_to_35] zope.proxy 3.4.2 py25_32
    DEBUG - Checking if build required for [zope.proxy_34_to_35] zope.proxy 3.4.2 py26_32
    DEBUG - Build not required for [zope.proxy_34_to_35] zope.proxy 3.4.2 py26_32
    DEBUG - Checking if build required for [zope.proxy_34_to_35] zope.proxy 3.5.0 py25_32
    DEBUG - Build not required for [zope.proxy_34_to_35] zope.proxy 3.5.0 py25_32
    DEBUG - Checking if build required for [zope.proxy_34_to_35] zope.proxy 3.5.0 py26_32
    DEBUG - Build not required for [zope.proxy_34_to_35] zope.proxy 3.5.0 py26_32
    INFO - Done.
    INFO -
    <BLANKLINE>
    ==================== ========== ========== ========== ==========
    zope.proxy           py24_32    py25_32    py26_32    py26_64
    ==================== ========== ========== ========== ==========
                   3.3.0 n/a        n/a        n/a        n/a
                   3.4.0 n/a        existed    done       n/a
                   3.4.1 n/a        done       failed     n/a
                   3.4.2 n/a        existed    existed    n/a
                   3.5.0 n/a        existed    existed    n/a
                   3.6.0 n/a        n/a        n/a        n/a

Let's see what was executed on mocks:

    >>> from pprint import pprint
    >>> pprint(testing.MOCKLOG)
    ['package_releases: zope.proxy',
     'urlget: http://pypi.python.org/simple/zope.proxy/',
     'cmd: svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.0 ...wineggbuilder in None',
     'cmd: ...bat in ...wineggbuilder',
     'cmd: svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.1 ...wineggbuilder in None',
     'cmd: ...bat in ...wineggbuilder',
     'cmd: ...bat in ...wineggbuilder']

Remove mocks:

    >>> base.SVN.commandKlass = oldSVNcommand
    >>> build.Compiler.commandKlass = oldCompilerCommand
    >>> build.Package.pypiKlass = oldPYPI
    >>> build.Package.urlGetterKlass = oldURLgetter
