"""
Let's create a Mammoth object in the root folder so we can access
views through the publisher:

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> root['manfred'] = Mammoth()

As an anonymous user, we only see the unprotected menu items:

  >>> from zope.testbrowser.testing import Browser
  >>> 1 + 1
  2
"""
import grok
from zope.component import getUtility

class Mammoth(grok.Model):
    pass

def test_suite():
    from zope.testing import doctest
    from megrok.storm.tests import FunctionalLayer
    suite = doctest.DocTestSuite()
    suite.layer = FunctionalLayer
    return suite
