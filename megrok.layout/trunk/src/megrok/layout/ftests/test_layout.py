"""
  >>> from megrok.layout import ILayout
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> mammoth = Mammoth()
  >>> mylayout = getMultiAdapter((request, mammoth), ILayout)
  >>> ILayout.providedBy(mylayout)
  True

  >>> mylayout.context
  <megrok.layout.ftests.test_layout.Mammoth object at ...>

  >>> mylayout.render()
  '<div> MyLayout </div>'

  >>> elephant = Elephant()
  >>> mycontextlayout = getMultiAdapter((request, elephant), ILayout)
  >>> mycontextlayout.render()
  '<div> MyContextLayout </div>'
"""

import grokcore.component as grok

from zope import interface
from megrok.layout import Layout


class Mammoth(grok.Context):
    pass


class Elephant(grok.Context):
    pass


class MyLayout(Layout):
    grok.context(interface.Interface)

    def render(self):
	return "<div> MyLayout </div>"


class MyContextLayout(Layout):
    grok.context(Elephant)

    def render(self):
	return "<div> MyContextLayout </div>"


def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite
