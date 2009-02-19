"""
  >>> from zope.component import getUtility
  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.template.interfaces import ILayoutTemplate
  >>> from zope.interface import Interface
  >>> from zope.component import getMultiAdapter
  >>> request = TestRequest()
  >>> house = House()
  >>> view = getMultiAdapter((house, request), name="myview")

Now call the view.

  >>> print view()
    <html>
       <body>
         <div class="layout"><html> <body> <div class="layout"> <div class="content"> my template content </div> </div> </body> </html></div>
       </body>
    </html>

"""
import grok
import megrok.pagelet
from zope.interface import Interface
from zope.component import getMultiAdapter
from z3c.pagelet.provider import PageletRenderer
from zope.contentprovider.interfaces import IContentProvider
import z3c.pagelet.interfaces
import zope.component
import zope.interface
import zope.publisher.interfaces.browser


class House(grok.Context):
    pass

class MyView(megrok.pagelet.Pagelet):
    grok.context(House)

    def render(self):
        return '<html> <body> <div class="layout"> <div class="content"> my template content </div> </div> </body> </html>'

class HouseLayout(megrok.pagelet.Layout):
    grok.context(House)
    megrok.pagelet.template('templates/house.pt')

class GPageletRenderer(grok.MultiAdapter, PageletRenderer):
    grok.implements(IContentProvider)
    grok.name('pagelet')
    grok.adapts(zope.interface.Interface,
                zope.publisher.interfaces.browser.IBrowserRequest,
		z3c.pagelet.interfaces.IPagelet)
    grok.provides(IContentProvider)

def test_suite():
    from zope.testing import doctest
    from megrok.pagelet.tests import FunctionalLayer
    import interlude
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
