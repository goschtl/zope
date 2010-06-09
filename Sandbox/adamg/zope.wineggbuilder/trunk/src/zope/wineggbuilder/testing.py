"""tests

$Id$
"""
__docformat__ = 'ReStructuredText'

import unittest
import doctest
import pprint

MOCKLOG = []

#format is [(expected cmd, result)]
CommandIO = [
#svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.6.0 /tmp/tmpgqt2dHwineggbuilder
"""A    /tmp/tmpgqt2dHwineggbuilder/bootstrap.py
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
Checked out revision 113298.""",
#svn co --non-interactive  svn://svn.zope.org/repos/main/zope.proxy/tags/3.4.1 /tmp/tmpKNdQxlwineggbuilder
"""A    /tmp/tmpKNdQxlwineggbuilder/bootstrap.py
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
Checked out revision 113298.""",
'svn co',
'svn co',
'bat',
'bat',
'bat',
'bat',
]

class MockCommand(object):
    def __init__(self):
        pass

    def __call__(self, cwd=None, captureOutput=True, exitOnError=True):
        self.cwd = cwd
        self.captureOutput = captureOutput
        self.exitOnError = exitOnError
        return self

    def do(self, cmd):
        global MOCKLOG
        MOCKLOG.append('cmd: %s in %s' % (cmd, self.cwd))

        global CommandIO
        next = CommandIO.pop(0)

        if isinstance(next, Exception):
            raise next

        return next

PYPI_RELEASES = {
    'zope.proxy': ['3.6.0', '3.5.0', '3.4.2', '3.4.1', '3.4.0', '3.3.0'],
}

class MockPYPI(object):
    def __init__(self):
        pass

    def __call__(self):
        return self

    #def list_packages(self):
    #    pass

    def package_releases(self, package_name, show_hidden=False):
        global MOCKLOG
        MOCKLOG.append('package_releases: %s' % package_name)

        return PYPI_RELEASES[package_name]

    #def release_urls(self, package_name, version):
    #    pass
    #
    #def release_data(self, package_name, version):
    #    pass
    #
    #def search(self, spec, operator=None):
    #    pass
    #
    #def changelog(self, since):
    #    pass

RESPONSES = {
    'http://pypi.python.org/simple/zope.proxy/' :
        """<html><head><title>Links for zope.proxy</title></head><body><h1>Links for zope.proxy</h1><a href="../../packages/source/z/zope.proxy/zope.proxy-3.6.0.zip#md5=896d9c53837d01875fe55cc69f43f7aa">zope.proxy-3.6.0.zip</a><br/>
<a href="../../packages/2.6/z/zope.proxy/zope.proxy-3.6.0-py2.6-win-amd64.egg#md5=8cb96ee292e127df8c4524ec486a05b6">zope.proxy-3.6.0-py2.6-win-amd64.egg</a><br/>
<a href="../../packages/2.6/z/zope.proxy/zope.proxy-3.5.0-py2.6-win-amd64.egg#md5=f3bdd81ef3d3f21db5cb4d9fe99b2b6e">zope.proxy-3.5.0-py2.6-win-amd64.egg</a><br/>
<a href="../../packages/2.6/z/zope.proxy/zope.proxy-3.5.0-py2.6-win32.egg#md5=ae9c7e9ecf949422abd98c23507636ac">zope.proxy-3.5.0-py2.6-win32.egg</a><br/>
<a href="../../packages/2.4/z/zope.proxy/zope.proxy-3.4.0-py2.4-win32.egg#md5=c23cda9412f8859d0d2d36c16e69a5a8">zope.proxy-3.4.0-py2.4-win32.egg</a><br/>
<a href="../../packages/source/z/zope.proxy/zope.proxy-3.4.0.tar.gz#md5=a9e234e90bc4a16bb62b967d4a0412c6">zope.proxy-3.4.0.tar.gz</a><br/>
<a href="../../packages/2.5/z/zope.proxy/zope.proxy-3.5.0-py2.5-win32.egg#md5=7ea1aa4dd320e9cceaae5031026259cc">zope.proxy-3.5.0-py2.5-win32.egg</a><br/>
<a href="../../packages/source/z/zope.proxy/zope.proxy-3.5.0.tar.gz#md5=ac5fc916b572bc3ff630b49cda52d94a">zope.proxy-3.5.0.tar.gz</a><br/>
<a href="../../packages/source/z/zope.proxy/zope.proxy-3.4.2.zip#md5=ad51f25d4d86be7cfebb70bd77421f92">zope.proxy-3.4.2.zip</a><br/>
<a href="../../packages/2.4/z/zope.proxy/zope.proxy-3.5.0-py2.4-win32.egg#md5=8c73b52e76f6aea17b1542b85d8b58f4">zope.proxy-3.5.0-py2.4-win32.egg</a><br/>
<a href="../../packages/2.6/z/zope.proxy/zope.proxy-3.4.2-py2.6-win32.egg#md5=3eff1609ba267b2b3becbe2eb37fb401">zope.proxy-3.4.2-py2.6-win32.egg</a><br/>
<a href="../../packages/2.4/z/zope.proxy/zope.proxy-3.4.1-py2.4-win32.egg#md5=02da4f1338131d7feffabe06488962c6">zope.proxy-3.4.1-py2.4-win32.egg</a><br/>
<a href="../../packages/source/z/zope.proxy/zope.proxy-3.4.1.zip#md5=b4d5c7345a7a2a60071a6f62db9592c6">zope.proxy-3.4.1.zip</a><br/>
<a href="../../packages/2.5/z/zope.proxy/zope.proxy-3.4.2-py2.5-win32.egg#md5=6c1661131b0dd8c8e667b47d1e7707e7">zope.proxy-3.4.2-py2.5-win32.egg</a><br/>
<a href="../../packages/2.4/z/zope.proxy/zope.proxy-3.4.2-py2.4-win32.egg#md5=67184719dfe56838be7241391721f11d">zope.proxy-3.4.2-py2.4-win32.egg</a><br/>
<a href="../../packages/2.5/z/zope.proxy/zope.proxy-3.4.0-py2.5-win32.egg#md5=aa0e2c00e011b026820630150ca028ba">zope.proxy-3.4.0-py2.5-win32.egg</a><br/>
<a href="../../packages/2.5/z/zope.proxy/zope.proxy-3.3.0-py2.5-win32.egg#md5=bcf3c132a36906787a07aac7226cbb1b">zope.proxy-3.3.0-py2.5-win32.egg</a><br/>
<a href="../../packages/source/z/zope.proxy/zope.proxy-3.3.0.tar.gz#md5=64128ab4feeb5bfd8a66c4cdd5192a31">zope.proxy-3.3.0.tar.gz</a><br/>
<a href="../../packages/2.6/z/zope.proxy/zope.proxy-3.6.0-py2.6-win32.egg#md5=6984986850f74abdb3cd0c738579cb16">zope.proxy-3.6.0-py2.6-win32.egg</a><br/>
<a href="../../packages/source/z/zope.proxy/zope.proxy-3.4.0.zip#md5=3fef9f29c8b920c9f20aa3a2f92afa70">zope.proxy-3.4.0.zip</a><br/>
<a href="../../packages/2.4/z/zope.proxy/zope.proxy-3.3.0-py2.4-win32.egg#md5=554d10d694d7e5ea9468d88c1c078387">zope.proxy-3.3.0-py2.4-win32.egg</a><br/>
<a href="../../packages/2.5/z/zope.proxy/zope.proxy-3.4.1-py2.5-win32.egg#md5=82c2d44d956ceaa1c838bf23be18fe95">zope.proxy-3.4.1-py2.5-win32.egg</a><br/>
<a href="http://svn.zope.org/zope.proxy" rel="homepage">3.3.0 home_page</a><br/>
<a href="http://docs.python.org/ref/sequence-methods.html">http://docs.python.org/ref/sequence-methods.html</a><br/>
</body></html>""",
}

class MockURLGetter(object):
    def __init__(self):
        pass

    def __call__(self):
        return self

    def get(self, url):
        global MOCKLOG
        MOCKLOG.append('urlget: %s' % url)
        return RESPONSES[url]