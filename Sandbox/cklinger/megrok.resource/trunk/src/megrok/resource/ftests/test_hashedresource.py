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

Here we proof if we get the resource "a.js" in the context
of a hashedresource.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/application/withhash')
  >>> print browser.contents
  <html>
    <head>
       <script type="text/javascript"
       src="http://localhost/@@/hasedstyles/++noop++05d3614435a4164676867ad1f1320cd2/@@/hasedstyles/a.js"></script>
   </head>
    <body>
       <h1> HI GROK </h1>
    </body>
  </html>  
"""


import grokcore.component as grok
import grokcore.view as view

from zope.interface import Interface
from megrok.resource import Library, include, inclusion, hashed
from hurry.resource import ResourceInclusion

from zope.app.container import btree

from zope.app.component.site import SiteManagerContainer

#class Application(btree.BTreeContainer):
class Application(SiteManagerContainer):
    """ Sample Application """

class HashedStyles(Library):
    view.path('css')
    grok.name('hasedstyles')
    hashed() 
    inclusion(name='JS', file='a.js')


class WithHash(view.View):
    grok.context(Interface)
    include(HashedStyles, 'JS')
    template = view.PageTemplateFile('templates/myview.pt')


###TestSetup
def test_suite():
    from zope.testing import doctest
    from megrok.resource.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite

