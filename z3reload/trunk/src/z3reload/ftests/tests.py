from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer
import doctest
import os
import unittest


Z3ReloadLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'Z3ReloadLayer', allow_teardown=True)


current_dir = os.path.dirname(__file__)


def openfile(filename, mode='r'):
    return file(os.path.join(current_dir, filename), mode)


def resetFile(test):
    dynamic_orig = openfile('dynamic_orig.py').read()
    openfile('dynamic.py', 'w').write(dynamic_orig)


def test_suite():
    optionflags = (doctest.ELLIPSIS | doctest.REPORT_NDIFF |
                   doctest.NORMALIZE_WHITESPACE)
    suite = FunctionalDocFileSuite('reload.txt', optionflags=optionflags,
                                   setUp=resetFile, tearDown=resetFile)
    suite.layer = Z3ReloadLayer
    return suite
