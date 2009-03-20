"""
  >>> from zope.component import getUtility
  >>> from z3c.template.interfaces import ILayoutTemplate 
  >>> from zope.publisher.browser import TestRequest
  >>> manfred = Mammoth()
  >>> from zope.interface import Interface
  >>> from zope.component import getMultiAdapter
  >>> request = TestRequest()
  >>> from zope.interface import Interface
  >>> elephant = Elephant()
  >>> layout = getMultiAdapter((elephant, request), ILayoutTemplate)
  >>> "<div> Layout </div>" in str(layout._read_file()) 
  True 


  >>> view = getMultiAdapter((elephant, request), name='mylayoutview')
  >>> print view()
  <div> Layout </div>

  >>> view = getMultiAdapter((manfred, request), name='mycontextlayoutview')
  >>> print view()
  <div> context layout </div>

"""
import grok
import megrok.pagelet
from zope.interface import Interface
from zope.component import getMultiAdapter
from z3c.template.interfaces import ILayoutTemplate

class Mammoth(grok.Context):
    pass

class Elephant(grok.Context):
    pass

class MyLayoutView(grok.View):
    grok.context(Elephant)
    layout = None

    def render(self):
        if self.layout is None:
            layout = getMultiAdapter(
                  (self.context, self.request), ILayoutTemplate)
            return layout(self)
        return self.layout()


class Layout(megrok.pagelet.Layout):
    grok.context(Elephant)
    #grok.name('layout')
    megrok.pagelet.template('templates/layout.pt')  

class MyContextLayoutView(grok.View):
    grok.context(Mammoth)
    layout = None

    def render(self):
        if self.layout is None:
            layout = getMultiAdapter(
                  (self.context, self.request), ILayoutTemplate)
            return layout(self)
        return self.layout()

class ContextLayout(megrok.pagelet.Layout):
    grok.context(Mammoth)
    megrok.pagelet.template('templates/context_layout.pt')

class NoTemplateLayout(megrok.pagelet.Layout):
    grok.context(Mammoth)
    megrok.pagelet.template('template/no_template.pt')


def test_suite():
    from zope.testing import doctest
    from megrok.pagelet.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
