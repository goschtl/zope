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
  >>> root['newapp'] = Application()

Our application has to be a Site to access the right url for the inclusions

  >>> root['newapp'].setSiteManager(LocalSiteManager(root['newapp']))
  >>> setSite(root['newapp'])
  >>> root['newapp']
  <megrok.resource.ftests.test_depends.Application object at ...>


Inclusion with dependency from a megrok.resource Library
--------------------------------------------------------

Now let's look if we can include the a.js File in a

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False 
  >>> browser.open('http://localhost/newapp/depends')
  >>> print browser.contents
  <html>
    <head>
      <script type="text/javascript" src="http://localhost/newapp/@@/basestyles/a.js"></script>
      <script type="text/javascript" src="http://localhost/newapp/@@/newstyles/b.js"></script>
   </head>
    <body>
       <h1> HI GROK </h1>
    </body>
  </html>  


Inclusion with a dependency from a hurry.core package
here we use hurry.jquery

  >>> browser.open('http://localhost/newapp/withjquery')
  >>> print browser.contents
  <html>
    <head>
      <script type="text/javascript" src="http://localhost/newapp/@@/jquery/jquery-1.3.2.js"></script>
  <script type="text/javascript" src="http://localhost/newapp/@@/newstyles/b.js"></script>
   </head>
    <body>
       <h1> HI GROK </h1>
    </body>
  </html>  

Here we include only hurry.jquery with no inclusion from megrok.resource.

  >>> browser.open('http://localhost/newapp/onlyjquery')
  >>> print browser.contents
  <html>
    <head>
      <script type="text/javascript" src="http://localhost/newapp/@@/jquery/jquery-1.3.2.js"></script>
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
from hurry.jquery import jquery


class Application(SiteManagerContainer):
    """ Sample Application """


class BaseStyles(Library):
    view.path('css')
    grok.name('basestyles')

    inclusion(name='JSBase', file='a.js')


class NewStyles(Library):
    view.path('css')
    grok.name('newstyles')
    
    inclusion(name='JSMore', file='b.js', depends=[BaseStyles.get('JSBase'),])
    inclusion(name='With_hurryjquery', file='b.js', depends=[jquery,])


class Depends(view.View):
    grok.context(Interface)
    include(NewStyles, 'JSMore')
    template = view.PageTemplateFile('templates/myview.pt')


class WithJquery(view.View):
    grok.context(Interface)
    include(NewStyles, 'With_hurryjquery')
    template = view.PageTemplateFile('templates/myview.pt')


class OnlyJquery(view.View):
    grok.context(Interface)
    include(jquery)
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

