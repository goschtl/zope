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
  >>> root['app'] = Application()

Our application has to be a Site to access the right url for the inclusions

  >>> root['app'].setSiteManager(LocalSiteManager(root['app']))
  >>> setSite(root['app'])
  >>> root['app']
  <megrok.resource.ftests.test_inclusion.Application object at ...>


ResourceDirectory
-----------------

If we create a Library we should get an fully registerd ResourceDirectory.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False 
  >>> browser.open('http://localhost/@@/styles/a.js')
  >>> print browser.contents
  /* Simple JS */ 


Inclusion
---------

Now let's look if we can include the a.js File in a

  >>> browser.open('http://localhost/app/simple')
  >>> print browser.contents
  <html>
    <head>
      <script type="text/javascript" src="http://localhost/app/@@/styles/a.js"></script>
   </head>
    <body>
       <h1> HI GROK </h1>
    </body>
  </html>  


AdvanceInclusion
----------------

  >>> browser.open('http://localhost/app/advanced')
  >>> print browser.contents
  <html>
    <head>
      <script type="text/javascript" src="http://localhost/app/@@/styles/a.js"></script>
   </head>
    <body>
       <h1> HI GROK </h1>
    <script type="text/javascript" src="http://localhost/app/@@/styles/b.js"></script></body>
  </html>    


Include All Inclusions
----------------------

  >>> browser.open('http://localhost/app/all')
  >>> print browser.contents
  <html>
    <head>
      <link rel="stylesheet" type="text/css" href="http://localhost/app/@@/styles/b.css" />
  <script type="text/javascript" src="http://localhost/app/@@/styles/a.js"></script>
  <script type="text/javascript" src="http://localhost/app/@@/styles/b.js"></script>
   </head>
    <body>
       <h1> HI GROK </h1>
    </body>
  </html> 
"""


import grokcore.component as grok
import grokcore.view as view

from zope.interface import Interface
from megrok.resource import Library, include, inclusion
from hurry.resource import ResourceInclusion

from zope.app.container import btree

from zope.app.component.site import SiteManagerContainer

#class Application(btree.BTreeContainer):
class Application(SiteManagerContainer):
    """ Sample Application """


class Styles(Library):
    view.path('css')
    grok.name('styles')
    
    inclusion(name='JS', file='a.js')
    inclusion(name='JSBottom', file='b.js', bottom=True)
    inclusion(name='CSS', file='b.css', bottom=True)


class Simple(view.View):
    grok.context(Interface)
    include(Styles, 'JS')
    template = view.PageTemplateFile('templates/myview.pt')


class Advanced(view.View):
    grok.context(Interface)
    include(Styles, 'JS')
    include(Styles, 'JSBottom', bottom=True)
    template = view.PageTemplateFile('templates/myview.pt')


class All(view.View):
    grok.context(Interface)
    template = view.PageTemplateFile('templates/myview.pt')
    include(Styles)




###TestSetup
def test_suite():
    from zope.testing import doctest
    from megrok.resource.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite

