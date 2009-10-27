# -*- coding: utf-8 -*-

import os.path
import unittest

from zope.testing import doctest
from zope.app.testing import functional
from grokcore.component.testing import grok_component

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True
    )

def test_suite():
    suite = unittest.TestSuite()
    readme = functional.FunctionalDocFileSuite(
        'README.txt',
        globs={
            '__name__': 'megrok.z3cform.composed.tests',
            'grok_component': grok_component
            }
        )
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
