# -*- coding: utf-8 -*-

import re
import os.path
import unittest

from pkg_resources import resource_listdir
from zope.testing import doctest, module
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True
    )

def setUp(test):
    module.setUp(test, 'megrok.z3cform.base.ftests')

def tearDown(test):
    module.tearDown(test)

def FsetUp(test):
    functional.FunctionalTestSetup().setUp()

def FtearDown(test):
    functional.FunctionalTestSetup().tearDown()


def test_suite():
    suite = unittest.TestSuite()
    readme = functional.FunctionalDocFileSuite(
            '../README.txt', setUp=setUp, tearDown=tearDown,
            optionflags=(doctest.ELLIPSIS+
                         doctest.NORMALIZE_WHITESPACE)
            )
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite

