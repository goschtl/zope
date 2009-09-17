"""
  >>> from five.megrok.layout import ILayout
  >>> from five.megrok.layout.ftests.layout.page import *
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest

  >>> request = TestRequest()
  >>> cow = Cow()

  The next line is for Zope 2. Don't fear it.
  >>> cow.REQUEST = request

  >>> mylayout = getMultiAdapter((request, cow), ILayout)
  >>> myview = getMultiAdapter((cow, request), name='myview')

  >>> print myview()
  <html>
   <body>
     <div class="layout"><p> My nice Content </p></div>
   </body>
  </html>

  >>> myview
  <five.megrok.layout.ftests.layout.page.MyView object at ...>
  >>> myview.layout
  <five.megrok.layout.ftests.layout.page.Master object at ...>
  >>> print myview.content()
  <p> My nice Content </p>

  >>> bigcow = BigCow()

  The next line is for Zope 2. Don't fear it.
  >>> bigcow.REQUEST = request

  >>> mybigview = getMultiAdapter((bigcow, request), name='myview')

  >>> print mybigview()
  <html>
   <body>
     <div class="layout"><p> My big cool Content </p>
  </div>
   </body>
  </html>

  >>> mybigview
  <five.megrok.layout.ftests.layout.page.MyBigView object at ...>
  >>> mybigview.layout
  <five.megrok.layout.ftests.layout.page.Master object at ...>
  >>> print mybigview.content()
  <p> My big cool Content </p>

"""
from five import grok

from zope import interface
from five.megrok.layout import Layout, Page


class Cow(grok.Context):
    pass


class BigCow(Cow):
    pass


class Master(Layout):
    grok.name('master')
    grok.context(Cow)


class MyView(Page):
    grok.context(interface.Interface)

    def render(self):
	return "<p> My nice Content </p>"


class MyBigView(Page):
    grok.name('myview')
    grok.context(BigCow)

