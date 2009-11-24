"""
  >>> from five.megrok.layout import ILayout
  >>> from five.megrok.layout.ftests.layout.layout import *
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.interface.verify import verifyObject

  >>> request = TestRequest()

You can create a context object and as a layout for it:

  >>> mammoth = Mammoth('arthur')
  >>> mylayout = getMultiAdapter((request, mammoth), ILayout)
  >>> mylayout
  <five.megrok.layout.ftests.layout.layout.MyLayout object at ...>
  >>> verifyObject(ILayout, mylayout)
  True
  >>> mylayout.context.aq_base
  <Mammoth at arthur>
  >>> mylayout.render()
  '<div> MyLayout </div>'

The layout can be different depending of the context:

  >>> elephant = Elephant('paul')
  >>> mycontextlayout = getMultiAdapter((request, elephant), ILayout)
  >>> mycontextlayout
  <five.megrok.layout.ftests.layout.layout.MyContextLayout object at ...>
  >>> mycontextlayout.context.aq_base
  <Elephant at paul>
  >>> mycontextlayout.render()
  '<div> MyContextLayout </div>'

"""

from five import grok

from zope import interface
from five.megrok.layout import Layout


class Mammoth(grok.Model):
    pass


class Elephant(grok.Model):
    pass


class MyLayout(Layout):
    grok.context(interface.Interface)

    def render(self):
        return "<div> MyLayout </div>"


class MyContextLayout(Layout):
    grok.context(Elephant)

    def render(self):
        return "<div> MyContextLayout </div>"

