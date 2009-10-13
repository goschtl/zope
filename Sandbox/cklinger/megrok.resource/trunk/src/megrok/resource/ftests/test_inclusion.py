"""
megrok.resource
===============


Setup
-----

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> root['app'] = grok.Application()

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
"""
import grok

from zope.interface import Interface
from megrok.resource import Library, include, inclusion, bottom
from hurry.resource import ResourceInclusion


class Styles(Library):
    grok.path('css')
    grok.name('styles')
    
    inclusion(name='JS', file='a.js')
    inclusion(name='JSBottom', file='b.js', bottom=True)
    inclusion(name='JSBottom', file='b.js', bottom=True)


class Simple(grok.View):
    grok.context(Interface)
    include(Styles, 'JS')
    template = grok.PageTemplateFile('templates/myview.pt')


class Advanced(grok.View):
    grok.context(Interface)
    include(Styles, 'JS')
    include(Styles, 'JSBottom')
    bottom()
    template = grok.PageTemplateFile('templates/myview.pt')


class All(grok.View):
    grok.context(Interface)
    template = grok.PageTemplateFile('templates/myview.pt')
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

