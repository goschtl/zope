import unittest
import doctest

from zope.sendmail.interfaces import IMailDelivery
import zope.component.testing
import zope.component.eventtesting
from zope.interface import implements

from grokstar.mail import notifyCommentAdded

class DummyMailDelivery(object):
    implements(IMailDelivery)
    def send(self, fromaddr, toaddr, msg):
        print msg
        
def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.eventtesting.setUp(test)
    zope.component.provideUtility(DummyMailDelivery(), name='grokstar')
    zope.component.provideHandler(notifyCommentAdded)
    
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('notifications.txt',
                             setUp=setUp,
                             tearDown=zope.component.testing.tearDown,
                             optionflags=doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')