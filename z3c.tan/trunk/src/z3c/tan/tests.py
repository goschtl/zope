import unittest
import zope.component
import zope.interface
from zope.testing import doctest
from zope.app.testing import setup

from zope.publisher.interfaces import IRequest
from zope.app.session.interfaces import ISession
from zope.app.session.session import RAMSessionDataContainer, SessionPkgData

sessionData = RAMSessionDataContainer()

class TestSession(object):
    """See zope.app.session.interfaces.ISession"""
    zope.interface.implements(ISession)
    zope.component.adapts(IRequest)

    def __init__(self, request):
        self.request = request

    def get(self, pkg_id, default=None):
        """See zope.app.session.interfaces.ISession"""
        return sessionData.get(pkg_id, default)

    def __getitem__(self, pkg_id):
        """See zope.app.session.interfaces.ISession"""
        if pkg_id not in sessionData:
            sessionData[pkg_id] = SessionPkgData()
        return sessionData[pkg_id]

def clearSessionData():
    global sessionData
    sessionData = RAMSessionDataContainer()

def setUp(test):
    setup.placefulSetUp()
    clearSessionData()

def tearDown(test):
    setup.placefulTearDown()
    clearSessionData()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            globs={'clearSessionData': clearSessionData},
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
