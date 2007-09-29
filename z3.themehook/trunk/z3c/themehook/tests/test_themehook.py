import os
import unittest
import zope.interface
import zope.component
import zope.app.testing
from zope.testbrowser.testing import Browser
from zope.app.testing import functional

from z3c.themehook.interfaces import IPublicationObjectCaller
from zope.publisher.interfaces.browser import IBrowserRequest

ThemeHookLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'ThemeHookLayer', allow_teardown=True)

class TestThemer(object):
    zope.interface.implements(IPublicationObjectCaller)
    zope.component.adapts(None, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        return 'TestThemer output'
    

class ThemeHookTest(functional.FunctionalTestCase):
    layer = ThemeHookLayer
    
    def test_themehook(self):
        # First test that things work with a hook
        browser = Browser()
        browser.open('http://localhost/')
        # Make sure it worked
        self.failUnless('Unauthenticated User' in browser.contents,
                    "Default caller broken")

        # Register the themer in the hook:
        zope.component.provideAdapter(TestThemer, (None, IBrowserRequest), 
                             IPublicationObjectCaller)
        
        # Now put in the theming:
        browser.open('http://localhost/')
        # Not it's the TestThemer that makes the output:
        self.failUnless('TestThemer output' in browser.contents,
                    'TestThemer output not found',)

def test_suite():
    from unittest import TestSuite, makeSuite
    
    suite = TestSuite()
    suite.addTests(makeSuite(ThemeHookTest))

    return suite

