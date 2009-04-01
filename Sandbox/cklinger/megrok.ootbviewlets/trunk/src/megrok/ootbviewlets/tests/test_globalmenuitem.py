"""
Set up a content object in the application root::

  >>> from zope.app.testing.functional import getRootFolder
  >>> from zope.app.component.hooks import setSite 
  >>> root = getRootFolder()
  >>> root['app'] = MyApp()
  >>> root['app']['klaus'] = MyContext()
  >>> setSite(root['app'])

Traverse to the view on the model object. We get the viewlets
registered for the default layer, with the anybody permission::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Open the myview in context of our application should give us
the logout link in the right context.

  >>> browser.open("http://localhost/app/@@myview")
  >>> print browser.contents
  <a href="http://localhost/app/logout.html"
     class="inactive-menu-item">logoutviewlet</a>

  >>> browser.open("http://localhost/app/klaus/@@myview")
  >>> print browser.contents
  <a href="http://localhost/app/logout.html"
     class="inactive-menu-item">logoutviewlet</a>

"""
import grok
from zope.interface import Interface
from megrok.ootbviewlets import GlobalMenuViewlet

class MyApp(grok.Application, grok.Container):
    pass

class MyContext(grok.Context):
    pass

class MyView(grok.View):
    grok.context(Interface)
    pass

class MyManager(grok.ViewletManager):
    grok.context(Interface)
    grok.name('mymanager')

class LogoutViewlet(GlobalMenuViewlet):
    grok.context(Interface)

    viewURL = 'logout.html'




def test_suite():
    from zope.testing import doctest
    from megrok.ootbviewlets.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_NDIFF)
    suite.layer = FunctionalLayer
    return suite

