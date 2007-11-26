from zope.testing import doctest
import unittest

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

import zope.component.testing
import zope.component.tests

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             optionflags=OPTIONFLAGS,
                             setUp=zope.component.testing.setUp,
                             tearDown=zope.component.testing.tearDown,
                             package="z3c.discriminator"),) + 

        # run test suite from zope.component to make sure
        # our patches are correct
 
        tuple(suite for suite in zope.component.tests.test_suite()),
    )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
