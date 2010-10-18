"""
  >>> from megrok.layout import ILayout
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> cow = Cow()
  >>> mylayout = getMultiAdapter((request, cow), ILayout)
  >>> myview = getMultiAdapter((cow, request), name='myview')


  >>> print myview()
  <html>
   <body>
     <div class="layout"><p> My nice Content </p></div>
   </body>
  </html>


  >>> myview
  <megrok.layout.ftests.test_page.MyView object at ...>
  >>> myview.layout
  <megrok.layout.ftests.test_page.Master object at ...>
  >>> print myview.content()
  <p> My nice Content </p>

"""
import grokcore.component as grok
from grokcore.view import templatedir

from zope import interface
from megrok.layout import Layout, Page, CodePage

templatedir('templates')


class Cow(grok.Context):
    pass


class Master(Layout):
    grok.name('master')
    grok.context(Cow)


class MyView(CodePage):
    grok.context(interface.Interface)

    def render(self):
	return "<p> My nice Content </p>"


def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite
