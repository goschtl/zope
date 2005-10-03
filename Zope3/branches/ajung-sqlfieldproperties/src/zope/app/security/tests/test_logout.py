import unittest

from zope.testing import doctest
from zope.interface import implements
from zope.component import provideAdapter, adapts
from zope.publisher.tests.httprequest import TestRequest

from zope.app.testing import placelesssetup
from zope.app.security import interfaces

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            '../logout.txt',
            globs={'provideAdapter': provideAdapter,
                   'TestRequest': TestRequest,
                   'implements': implements,
                   'adapts': adapts,
                   'IAuthentication': interfaces.IAuthentication
                  },
            setUp=placelesssetup.setUp,
            tearDown=placelesssetup.tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
