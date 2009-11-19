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
  >>> root['simpleapp'] = Application()

Our application has to be a Site to access the right url for the inclusions

  >>> root['simpleapp'].setSiteManager(LocalSiteManager(root['simpleapp']))
  >>> setSite(root['simpleapp'])
  >>> root['simpleapp']
  <megrok.resource.ftests.test_mf.Application object at ...>


ResourceDirectory
-----------------

If we create a Library we should get an fully registerd ResourceDirectory.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False 
  >>> browser.open('http://localhost/@@/mylibrary/a.js')
  >>> print browser.contents
  /* Simple JS */ 

For default we can access these resources with the help of z3c.hashedresource
First we have to get the hash to look for the resource in the testbrowser.

   >>> from zope.component import getAdapter
   >>> from zope.publisher.browser import TestRequest
   >>> library = getAdapter(TestRequest(), name='mylibrary')
   >>> library
   <grokcore.view.components.DirectoryResource object at ...>

   >>> from z3c.hashedresource.interfaces import IResourceContentsHash
   >>> hash = IResourceContentsHash(library)
   
   >>> ajs = 'http://localhost/@@/++noop++%s/mylibrary/a.js' % hash
   >>> browser.open(ajs)
   >>> print browser.contents
   /* Simple JS */

  >>> browser.open('http://localhost/simpleapp/simpleview')
  >>> stag%(hash) in browser.contents 
  True

  >>> print browser.contents 
  <html>
    <head>
   ...
   </head>
    <body>
       <h1> HI GROK </h1>
    </body>
  </html>  


"""

stag = '<script type="text/javascript" src="http://localhost/simpleapp/@@/++noop++%s/mylibrary/a.js"></script>'

import grokcore.component as grok
import grokcore.view as view

from megrok import resource
from zope.interface import Interface
from zope.app.component.site import SiteManagerContainer
from hurry.resource import ResourceInclusion

class Application(SiteManagerContainer):
    """ Sample Application """


class MyLibrary(resource.Library):
    resource.path('css')
    resource.name('mylibrary')
    
myjs = ResourceInclusion(MyLibrary, 'a.js')    


class SimpleView(view.View):
    grok.context(Interface)
    resource.need(myjs)
    resource.not_hashed()
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

