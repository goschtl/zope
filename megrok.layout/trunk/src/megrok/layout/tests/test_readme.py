# -*- coding: utf-8 -*-

import doctest
import unittest
import megrok.layout.tests
from zope.testing import cleanup, module
from grokcore.component.testing import grok_component


def moduleSetUp(test):
    megrok.layout.tests.grok('megrok.layout')


def moduleTearDown(test):
    module.tearDown(test)
    cleanup.cleanUp()


def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {'grok_component': grok_component, '__name__': 'megrok.layout'}
    suite = unittest.TestSuite()

    suite.addTest(
        doctest.DocFileSuite(
            '../README.txt',
            optionflags=optionflags,
            setUp=moduleSetUp,
            tearDown=moduleTearDown,
            globs=globs))

    return suite
