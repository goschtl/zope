import unittest
from zope.testing.doctest import DocFileSuite, DocTestSuite

def test_BuddyInfo():
    """
    This view mainly provides access to city and state
    information for a buddy.  It relies on having a
    buddy that is adaptable to IPostalInfo.  Imagine we
    have a buddy that already implements IPostalInfo:

      >>> import zope.interface
      >>> from buddydemo.interfaces import IPostalInfo
      >>> class FakeBuddy:
      ...     zope.interface.implements(IPostalInfo)
      ...     city = 'Cleveland'
      ...     state = 'Ohio'
      >>> fake = FakeBuddy()

    We should be able to create a BuddyInfo on this
    fake buddy and get the right city and state back:

      >>> from buddydemo.browser import BuddyInfo
      >>> info = BuddyInfo(fake, 42)
      >>> info.city, info.state
      ('Cleveland', 'Ohio')

    We cheated a bit and used 42 as the request.

    As with all views, we expect to be able to access
    the thing being viewed and the request:

      >>> info.context is fake
      True
      >>> info.request
      42
    """

def test_BuddyRename():
    r"""
    This view provides a method for changing buddies.
    It is the action of a form in rename.html and
    redirects back there when it's done.

    Use a fake buddy class:

      >>> import zope.interface
      >>> class FakeBuddy:
      ...     first = 'bob'
      ...     last = 'smoth'
      >>> fake = FakeBuddy()

    Because the view needs to redirect, we have to give
    it a request:

      >>> from zope.publisher.browser import TestRequest
      >>> request = TestRequest()

    Our rename view is going to generate an event. Because
    of that, we need to setup an event service:

      >>> from zope.app.testing import placelesssetup
      >>> placelesssetup.setUp()
      
    We should be able to create a BuddyRename on this
    fake buddy and change it's name:

      >>> from buddydemo.browser import BuddyRename
      >>> rename = BuddyRename(fake, request)
      >>> rename.update('Bob', 'Smith')
      >>> fake.first, fake.last
      ('Bob', 'Smith')

    Make sure it redirected to rename.html:
    
      >>> request.response.getStatus()
      302
      >>> request.response.getHeader('location')
      'rename.html'

    There should be an ObjectModifiedEvent event logged:

      >>> from zope.app.event.tests.placelesssetup \
      ...      import getEvents
      >>> from zope.app.event.interfaces \
      ...      import IObjectModifiedEvent
      >>> [event] = getEvents(IObjectModifiedEvent)
      >>> event.object is fake
      True

    Finally, we'll put things back the way we found them:

      >>> placelesssetup.tearDown()
    """

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocFileSuite('buddy.txt'))
    suite.addTest(DocTestSuite('buddydemo.buddy'))
    suite.addTest(DocTestSuite('buddydemo.stubpostal'))
    suite.addTest(DocTestSuite())
    return suite
