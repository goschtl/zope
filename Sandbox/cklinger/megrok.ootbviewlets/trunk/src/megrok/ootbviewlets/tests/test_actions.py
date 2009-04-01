"""
Set up a content object in the application root::

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> root['actions'] = MyContext()

Traverse to the view on the model object. We get the viewlets
registered for the default layer, with the anybody permission::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser('http://localhost/actions/@@myview')
  >>> browser.handleErrors = True 

Open the myview in context of fred should give us
the print in link in the right context.

  >>> #browser.open("http://localhost/actions/@@myview")
  >>> print browser.contents
  <div class="actionMenuWrapper">
    <ul class="actionMenu">
      <li class="inactive-menu-item">
    <a href="http://localhost/actions/print"> 
      <div>print</div>
    </a>
  </li>
  <BLANKLINE>
    </ul>
  </div>
  <div class="clearActionMenu" />
  <BLANKLINE>
  <BLANKLINE>
"""
import grok
from megrok.ootbviewlets import ActionItem, ActionMenu 

class MyContext(grok.Context):
    pass

class MyView(grok.View):
    pass

class MyManager(ActionMenu):
    grok.name('mymanager')

class MyTab(ActionItem):
    grok.name('print')

    urlEndings = ['print', ]
    viewURL = 'print'

def test_suite():
    from zope.testing import doctest
    from megrok.ootbviewlets.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_NDIFF)
    suite.layer = FunctionalLayer
    return suite
