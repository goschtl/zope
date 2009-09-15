"""
  >>> from five.megrok.layout import ILayout
  >>> from five.megrok.layout.ftests.layout.resources import *
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest

  >>> request = TestRequest()
  >>> mongo = Dummy()
  >>> mylayout = getMultiAdapter((request, mongo), ILayout)
  >>> mylayout.static
  <five.grok.components.ZopeTwoDirectoryResource object at ...>
  >>> mylayout.static['empty.js']
  <Products.Five.browser.resource.FileResource object at ...>
"""

from five import grok
from five.megrok.layout import Layout


class Dummy(grok.Context):
    pass


class LayoutWithResources(Layout):

    def render(self):
        return ""
