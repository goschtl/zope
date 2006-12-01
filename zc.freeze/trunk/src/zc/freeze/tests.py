import unittest
from zope.app.testing import placelesssetup
import zope.testing.module
from zope.testing import doctest
from zope.component import testing, eventtesting
from zope.app.container.tests.placelesssetup import PlacelessSetup

container_setup = PlacelessSetup()

def setUp(test):
    placelesssetup.setUp(test)
    events = test.globs['events'] = []
    import zope.event
    zope.event.subscribers.append(events.append)

def tearDown(test):
    placelesssetup.tearDown(test)
    events = test.globs.pop('events')
    import zope.event
    assert zope.event.subscribers.pop().__self__ is events
    del events[:] # being paranoid

def subscribersSetUp(test):
    placelesssetup.setUp(test)
    zope.testing.module.setUp(test, 'zc.freeze.subscribers_txt')

def subscribersTearDown(test):
    zope.testing.module.tearDown(test)
    placelesssetup.tearDown(test)

def copierSetUp(test):
    zope.testing.module.setUp(test, 'zc.freeze.copier_txt')
    testing.setUp(test)
    eventtesting.setUp(test)
    container_setup.setUp()

def copierTearDown(test):
    zope.testing.module.tearDown(test)
    testing.tearDown(test)

def test_suite():
    tests = (
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'copier.txt',
            setUp=copierSetUp,
            tearDown=copierTearDown),
        )
    try:
        import zope.locking
    except ImportError:
        pass
    else:
        tests += (
        doctest.DocFileSuite(
            'subscribers.txt',
            setUp=subscribersSetUp, tearDown=subscribersTearDown,
            optionflags=doctest.INTERPRET_FOOTNOTES),)
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
