"""tests

$Id$
"""
__docformat__ = 'ReStructuredText'

import unittest
from zope.testing import doctest
#import doctest
import pprint

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('test.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     globs={'pprint': pprint}
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
