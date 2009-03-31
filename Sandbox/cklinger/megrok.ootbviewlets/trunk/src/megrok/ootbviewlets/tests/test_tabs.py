"""
Set up a content object in the application root::

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> root['tabs'] = MyContext()

Traverse to the view on the model object. We get the viewlets
registered for the default layer, with the anybody permission::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Open the myview in context of fred should give us
the print in link in the right context.

  >>> browser.open("http://localhost/tabs/@@myview")
  >>> print browser.contents
  &lt;div class="tabMenu"&gt;
    &lt;span class="inactive-menu-item"&gt;
    &lt;a href=""&gt;print&lt;/a&gt;
  &lt;/span&gt;
  <BLANKLINE>
  &lt;/div&gt;
  klaus


"""
import grok
from megrok.ootbviewlets import TabItem, TabMenuManager 

class MyContext(grok.Context):
    pass

class MyView(grok.View):
    pass

class MyManager(TabMenuManager):
    grok.name('mymanager')

class MyTab(TabItem):
    grok.name('print')

    urlEndings = ['print', ]
    viewURL = 'print'

def test_suite():
    from zope.testing import doctest
    from megrok.ootbviewlets.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_NDIFF)
    suite.layer = FunctionalLayer
    return suite

