"""$Id$
"""
import unittest
from zope.testing import doctest
from zope.app.tests import placelesssetup, ztapi
from zope.app.event.tests.placelesssetup import getEvents


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=placelesssetup.setUp,
                             tearDown=placelesssetup.tearDown,
                             globs={'provideUtility': ztapi.provideUtility,
                                    'getEvents': getEvents,
                                    },
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

