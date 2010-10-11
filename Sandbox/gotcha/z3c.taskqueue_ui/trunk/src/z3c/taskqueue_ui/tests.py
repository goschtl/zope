__docformat__ = 'restructuredtext'
import unittest
from zope.app.testing import functional
import os
import random

zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')

RemotetaskLayer = None #to please pyflakes
functional.defineLayer('RemotetaskLayer',
    zcml, allow_teardown=True)


def setUp(test):
    random.seed(27)


def tearDown(test):
    random.seed()


def test_suite():
    suite = functional.FunctionalDocFileSuite(
        os.sep.join(('browser', 'README.txt')),
        setUp=setUp,
        tearDown=tearDown,
    )
    suite.layer = RemotetaskLayer
    return unittest.TestSuite((suite, ))
