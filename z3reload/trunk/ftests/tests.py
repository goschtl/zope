import os
import unittest

from zope.testing import doctest
from zope.app.testing.functional import FunctionalDocFileSuite


current_dir = os.path.dirname(__file__)

def openfile(filename, mode='r'):
    return file(os.path.join(current_dir, filename), mode)

def resetFile(test):
    dynamic_orig = openfile('dynamic_orig.py').read()
    openfile('dynamic.py', 'w').write(dynamic_orig)


def test_suite():
    optionflags = (doctest.ELLIPSIS | doctest.REPORT_NDIFF |
                   doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_ONLY_FIRST_FAILURE)
    return FunctionalDocFileSuite('reload.txt', optionflags=optionflags,
                                  setUp=resetFile, tearDown=resetFile)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
