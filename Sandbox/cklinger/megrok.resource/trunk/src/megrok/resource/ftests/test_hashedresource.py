"""
megrok.resource
===============


Setup
-----

  >>> from zope.app.testing.functional import getRootFolder
  >>> from zope.app.container import btree
  >>> from zope.app.component.site import LocalSiteManager
  >>> from zope.app.component.hooks import setSite

  >>> root = getRootFolder()
  >>> root['application'] = Application()


Inclusion with z3c.hashedresource
---------------------------------

First we get the hash for the HashedStyle Library to compare it
with the inclusion we get in the page.

   >>> from zope.component import getAdapter
   >>> from zope.publisher.browser import TestRequest
   >>> library = getAdapter(TestRequest(), name='hashedstyles')
   >>> library
   <grokcore.view.components.DirectoryResource object at ...>

   >>> from z3c.hashedresource.interfaces import IResourceContentsHash
   >>> hash = IResourceContentsHash(library)
   

Here we proof if we get the resource "a.js" in the context
of a hashedresource.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> ajs = 'http://localhost/++noop++%s/@@/hashedstyles/a.js' % hash
  >>> browser.open(ajs)
  >>> print browser.contents
  /* Simple JS */
"""

import grokcore.component as grok
import grokcore.view as view

from zope.app.container import btree
from zope.interface import Interface
from hurry.resource import ResourceInclusion
from zope.app.component.site import SiteManagerContainer
from megrok.resource import Library, include, inclusion, hashed


class Application(SiteManagerContainer):
    """ Sample Application """

class HashedStyles(Library):
    view.path('css')
    grok.name('hashedstyles')
    hashed() 
    inclusion(name='JS', file='a.js')


###TestSetup
def test_suite():
    from zope.testing import doctest
    from megrok.resource.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite

