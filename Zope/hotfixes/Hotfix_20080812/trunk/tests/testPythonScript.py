##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import os, unittest, warnings

from Products.PythonScripts.PythonScript import PythonScript
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from RestrictedPython.tests.verify import verify


if __name__=='__main__':
    here = os.getcwd()
else:
    here = os.path.dirname(__file__)
    if not here:
        here = os.getcwd()

class WarningInterceptor:

    _old_stderr = None
    _our_stderr_stream = None

    def _trap_warning_output( self ):

        if self._old_stderr is not None:
            return

        import sys
        from StringIO import StringIO

        self._old_stderr = sys.stderr
        self._our_stderr_stream = sys.stderr = StringIO()

    def _free_warning_output( self ):

        if self._old_stderr is None:
            return

        import sys
        sys.stderr = self._old_stderr

# Test Classes

def readf(name):
    path = os.path.join(here, 'tscripts', '%s.ps' % name)
    return open(path, 'r').read()

class VerifiedPythonScript(PythonScript):

    def _newfun(self, code):
        verify(code)
        return PythonScript._newfun(self, code)


class PythonScriptTestBase(unittest.TestCase):
    def setUp(self):
        newSecurityManager(None, None)

    def tearDown(self):
        noSecurityManager()

    def _newPS(self, txt, bind=None):
        ps = VerifiedPythonScript('ps')
        ps.ZBindings_edit(bind or {})
        ps.write(txt)
        ps._makeFunction()
        if ps.errors:
            raise SyntaxError, ps.errors[0]
        return ps

    def _filePS(self, fname, bind=None):
        ps = VerifiedPythonScript(fname)
        ps.ZBindings_edit(bind or {})
        ps.write(readf(fname))
        ps._makeFunction()
        if ps.errors:
            raise SyntaxError, ps.errors[0]
        return ps

class TestPythonScriptNoAq(PythonScriptTestBase):

    def testRaiseSystemExitLaunchpad257269(self):
        ps = self._newPS("raise SystemExit")
        self.assertRaises(ValueError, ps)

    def testEncodingTestDotTestAllLaunchpad257276(self):
        ps = self._newPS("return 'foo'.encode('test.testall')")
        self.assertRaises(LookupError, ps)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPythonScriptNoAq))
    return suite


def main():
    unittest.TextTestRunner().run(test_suite())


if __name__ == '__main__':
    main()
