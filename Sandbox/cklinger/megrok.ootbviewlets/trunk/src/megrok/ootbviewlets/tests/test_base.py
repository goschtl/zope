"""
Set up a content object in the application root::

  >>> from zope.app.testing.functional import getRootFolder
  >>> from zope.app.component.hooks import setSite 
  >>> root = getRootFolder()
  >>> root['base'] = App()
  >>> setSite(root['base'])

Traverse to the view on the model object. We get the viewlets
registered for the default layer, with the anybody permission::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

The GlobalMenuItem should now act as a normal grok.Viewlet.
This means it should not return the GlobalMenuItem, it should 
return a simple <p> tag. This demonstrates that the normal
update render pattern, known from grok.Viewlet works
as expected.

  >>> browser.open("http://localhost/base/@@myview")
  >>> print browser.contents
  <p> This message was stored in the update method </p>
"""
import grok
from zope.interface import Interface
from megrok.ootbviewlets import GlobalMenuItem

class App(grok.Application, grok.Container):
    pass

class MyView(grok.View):
    pass

class MyManager(grok.ViewletManager):
    grok.name('mymanager')

class CustomViewlet(GlobalMenuItem):

    viewURL = 'logout.html'

    def update(self):
	self.message = "This message was stored in the update method"

    def render(self):
	return "<p> %s </p>" %self.message

def test_suite():
    from zope.testing import doctest
    from megrok.ootbviewlets.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_NDIFF)
    suite.layer = FunctionalLayer
    return suite

