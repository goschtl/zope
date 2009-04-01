"""
Set up a content object in the application root::

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> root['fred'] = MyContext()
  >>> root['klaus'] = MyContext()

Traverse to the view on the model object. We get the viewlets
registered for the default layer, with the anybody permission::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Open the myview in context of fred should give us
the print in link in the right context.

  >>> browser.open("http://localhost/fred/@@myview")
  >>> print browser.contents
  <a href="http://localhost/fred/print"
     class="inactive-menu-item">printviewlet</a>

Now look if we get the right link in the context of klaus too

  >>> browser.open("http://localhost/klaus/@@myview")
  >>> print browser.contents
  <a href="http://localhost/klaus/print"
     class="inactive-menu-item">printviewlet</a>

Now check if we get the right css class if we had the same url
endings in our view and the urlEndings in our Viewlet

  >>> browser.open("http://localhost/klaus/@@print")
  >>> print browser.contents
  <a href="http://localhost/klaus/print"
     class="active-menu-item">printviewlet</a>

"""
import grok
from megrok.ootbviewlets import ContextViewlet

class MyContext(grok.Context):
    pass

class MyView(grok.View):
    pass

class Print(grok.View):
    pass

class MyManager(grok.ViewletManager):
    grok.name('mymanager')

class PrintViewlet(ContextViewlet):

    urlEndings = ['print', ]
    viewURL = 'print'




def test_suite():
    from zope.testing import doctest
    from megrok.ootbviewlets.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_NDIFF)
    suite.layer = FunctionalLayer
    return suite

