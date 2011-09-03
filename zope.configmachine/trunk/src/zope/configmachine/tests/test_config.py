##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
"""Test configuration machinery.
"""

import os
import sys
import unittest
import re

import zope.interface
import zope.configmachine

from zope.configmachine.exceptions import ConfigurationError

class TestConfigurationContext(unittest.TestCase):
    def _makeOne(self):
        from zope.configmachine import ConfigurationContext
        return ConfigurationContext()

    def tearDown(self):
        for name in ('zope.configmachine.tests.victim',
                     'zope.configmachine.tests.bad'):
            if name in sys.modules:
                del sys.modules[name]

    def test_resolve_simple(self):
        import zope
        c = self._makeOne()
        c.resolve('zope') is zope

    def test_resolve_missing(self):
        c = self._makeOne()
        self.assertRaises(ConfigurationError,
                          c.resolve, 'zope.configmachine.eek')

    def test_resolve_starting_dot_no_package(self):
        c = self._makeOne()
        self.assertRaises(AttributeError, c.resolve, '.foo')

    def test_resolve_starting_dot_with_package(self):
        import zope
        c = self._makeOne()
        c.package = zope
        result = c.resolve('.configmachine')
        self.assertEqual(result, zope.configmachine)

    def test_resolve_starting_double_dot_with_package(self):
        c = self._makeOne()
        c.package = zope.interface
        result = c.resolve('..configmachine')
        self.assertEqual(result, zope.configmachine)

    def test_resolve_dot_no_package(self):
        c = self._makeOne()
        self.assertRaises(AttributeError, c.resolve, '.')

    def test_resolve_builtin(self):
        c = self._makeOne()
        result = c.resolve('type')
        self.assertEqual(result, type)

    def test_resolve_dot_with_package(self):
        import zope
        c = self._makeOne()
        c.package = zope
        result = c.resolve('.')
        self.assertEqual(result, zope)
        
    def test_resolve_trailing_dot(self):
        c = self._makeOne()
        self.assertRaises(ValueError, c.resolve, 'zope.')

    def test_resolve_blank(self):
        c = self._makeOne()
        self.assertRaises(ValueError, c.resolve, '   ')

    def test_resolve_bad_dotted_last_import(self):
        c = self._makeOne()
        self.assertRaises(ConfigurationError, c.resolve,
                          'zope.configmachine.tests.nosuch')

    def test_resolve_bad_dotted_import(self):
        c = self._makeOne()
        self.assertRaises(ConfigurationError,
                          c.resolve, 'zope.configmachine.nosuch.noreally')

    def test_resolve_bad_sub_last_import(self):
        c = self._makeOne()
        self.assertRaises(ImportError, c.resolve,
                          'zope.configmachine.tests.victim')

    def test_resolve_bad_sub_import(self):
        c = self._makeOne()
        self.assertRaises(ImportError, c.resolve,
                          'zope.configmachine.tests.victim.nosuch')

    def test_path_abs(self):
        c = self._makeOne()
        self.assertEqual(c.path('/x/y/z'), os.path.normpath('/x/y/z'))

    def test_path_relative_no_package(self):
        c = self._makeOne()
        self.assertRaises(AttributeError, c.path, 'y/z')

    def test_path_relative_with_package(self):
        c = self._makeOne()
        c.package = zope.configmachine
        d = os.path.dirname(zope.configmachine.__file__)
        self.assertEqual(c.path('y/z'), d + os.path.normpath('/y/z'))
        self.assertEqual(c.path('y/./z'), d + os.path.normpath('/y/z'))
        self.assertEqual(c.path('y/../z'), d + os.path.normpath('/z'))

    def test_path_basepath_absolute(self):
        class stub:
            __file__ = os.path.join('relative', 'path')
        c = self._makeOne()
        c.package = stub()
        self.assertTrue(os.path.isabs(c.path('y/z')))

    def test_path_basepath_uses_dunder_path(self):
        class stub:
            __path__ = [os.path.join('relative', 'path')]
        c = self._makeOne()
        c.package = stub()
        self.assertTrue(os.path.isabs(c.path('y/z')))

    def test_checkDuplicate_simple(self):
        c = self._makeOne()
        self.assertEqual(c.checkDuplicate('/foo.zcml'), None)
        self.assertRaises(ConfigurationError, c.checkDuplicate, '/foo.zcml')

    def test_checkDuplicate_aliases(self):
        d = os.path.dirname(zope.configmachine.__file__)
        c = self._makeOne()
        c.package = zope.configmachine
        self.assertEqual(c.checkDuplicate('bar.zcml'), None)
        self.assertRaises(ConfigurationError, c.checkDuplicate,
                          d + os.path.normpath('/bar.zcml'))

    def test_processFile_simple(self):
        c = self._makeOne()
        self.assertTrue(c.processFile('/foo.zcml'))
        self.assertFalse(c.processFile('/foo.zcml'))

    def test_processFile_alias(self):
        d = os.path.dirname(zope.configmachine.__file__)
        c = self._makeOne()
        c.package = zope.configmachine
        self.assertTrue(c.processFile('/foo.zcml'))
        self.assertFalse(c.checkDuplicate(d + os.path.normpath('/foo.zcml')))

    def test_action_simple(self):
        from zope.configmachine.tests.directives import f
        c = self._makeOne()
        c.actions = []
        c.action(1, f, (1,), {'x':1})
        self.assertEqual(c.actions, [(1, f, (1,), {'x': 1})])
        c.action(None)
        self.assertEqual(c.actions, [(1, f, (1,), {'x': 1}), (None, None)])

    def test_action_with_includepath_and_info(self):
        c = self._makeOne()
        c.actions = []
        c.includepath = ('foo.zcml',)
        c.info = '?'
        c.action(None)
        self.assertEqual(c.actions,
                         [(None, None, (), {}, ('foo.zcml',), '?')])

    def test_action_with_order(self):
        c = self._makeOne()
        c.actions = []
        c.action(None, order=99999)
        self.assertEqual(c.actions, [(None, None, (), {}, (), '', 99999)])

    def test_action_with_includepath_dynamic(self):
        c = self._makeOne()
        c.actions = []
        c.action(None, includepath=('abc',))
        self.assertEqual(c.actions, [(None, None, (), {}, ('abc',))])

    def test_action_with_info_dynamic(self):
        c = self._makeOne()
        c.actions = []
        c.action(None, info='abc')
        self.assertEqual(c.actions, [(None, None, (), {}, (), 'abc')])

    def test_hasFeature(self):
        c = self._makeOne()
        self.assertFalse(c.hasFeature('onlinehelp'))
        c._features.add('onlinehelp')
        self.assertTrue(c.hasFeature('onlinehelp'))

    def test_provideFeature(self):
        c = self._makeOne()
        self.assertEqual(list(c._features), [])
        c.provideFeature('foo')
        self.assertEqual(list(c._features), ['foo'])

def test_suite(): # pragma: no cover
    from doctest import DocTestSuite
    from zope.testing import renormalizing
    checker = renormalizing.RENormalizing([
        (re.compile(r"<type 'exceptions.(\w+)Error'>:"),
                    r'exceptions.\1Error:'),
        ])
    suite = unittest.TestSuite((
        DocTestSuite('zope.configmachine',checker=checker),
        unittest.TestLoader().loadTestsFromTestCase(TestConfigurationContext),
        DocTestSuite(),
        ))
    return suite

if __name__ == '__main__': unittest.main()
