##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the workflow ZCML namespace directives.

$Id$
"""
import unittest

from zope.app.interpreter.interfaces import IInterpreter
from zope.app.interpreter.python import PythonInterpreter
from zope.security.interfaces import ForbiddenAttribute
from zope.interface.verify import verifyObject

class PythonInterpreterTest(unittest.TestCase):

    def _check(self, code, output, raw=False):
        if raw:
            func = PythonInterpreter.evaluateRawCode
        else:
            func = PythonInterpreter.evaluate
        self.globals = {}
        self.assertEqual(func(code, self.globals), output)

    def test_verifyInterface(self):
        self.assert_(verifyObject(IInterpreter, PythonInterpreter))

    def test_simple(self):
        self._check('print "hello"', 'hello\n')
        self._check('print "hello"', 'hello\n', True)

    def test_indented(self):
        self._check('\n  print "hello"\n', 'hello\n', True)

    def test_multi_line(self):
        code = ('print "hello"\n'
                'print "world"\n')
        self._check(code, 'hello\nworld\n')
        self._check(code, 'hello\nworld\n', True)
        code = ('  print "hello"\n'
                '  print "world"\n')
        self._check(code, 'hello\nworld\n', True)

    def test_variable_assignment(self):
        code = ('x = "hello"\n'
                'print x')
        self._check(code, 'hello\n')
        self._check(code, 'hello\n', True)

    def test_local_variable_assignment(self):
        code = ('x = "hello"\n')
        self._check(code, '')
        self.assert_('x' not in self.globals.keys())

# TODO: get global statements working
# The compiler module, which we now rely on, doesn't handle global
# statements correctly.
##     def test_global_variable_assignment(self):
##         code = ('global x\n'
##                 'x = "hello"\n')
##         self._check(code, '')
##         self.assertEqual(self.globals['x'], 'hello')

    def test_wrapped_by_html_comment(self):
        self._check('<!-- print "hello" -->', 'hello\n', True)
        self._check('<!--\nprint "hello"\n -->', 'hello\n', True)
        self._check('<!--\n  print "hello"\n -->', 'hello\n', True)

    def test_forbidden_attribute(self):
        code = ('import sys\n'
                'print sys.path\n')
        self.assertRaises(ForbiddenAttribute,
                          PythonInterpreter.evaluateRawCode, code, {})

    def test_windows_newline(self):
        code = ('print "hello"\r\n'
                'print "world"\r\n')
        self._check(code, 'hello\nworld\n', True)
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PythonInterpreterTest),
        ))

if __name__ == '__main__':
    unittest.main()
