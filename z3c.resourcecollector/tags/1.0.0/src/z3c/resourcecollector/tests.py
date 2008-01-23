__docformat__ = "reStructuredText"

import doctest
import unittest
from zope.testing import doctest

from zope.testing.doctestunit import DocFileSuite, DocTestSuite
import os

here = os.path.dirname(__file__)

def test_suite():
    return unittest.TestSuite(
        (
        DocFileSuite('zcml.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

