"""
  Some requirements:
  >>> from five.megrok.layout import IPage
  >>> from five.megrok.layout.ftests.layout.page import *
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.interface.verify import verifyObject

  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> request = TestRequest()
  >>> root = getRootFolder()
  >>> root["cow"] = Cow(id='cow')
  >>> cow = root["cow"]

  You can now a page:
  >>> myview = getMultiAdapter((cow, request), name='myview')
  >>> myview
  <five.megrok.layout.ftests.layout.page.MyView object at ...>
  >>> IPage.providedBy(myview)
  True

  You can render your page, it's going to look for a layout and use it
  to render itself:
  >>> print myview()
  <html>
   <body>
     <div class="layout"><p> My nice Content </p></div>
   </body>
  </html>
  >>> myview.layout
  <five.megrok.layout.ftests.layout.page.Master object at ...>
  >>> print myview.content()
  <p> My nice Content </p>

  Here an another example:
  >>> id = root._setObject("bigcow", BigCow(id='bigcow'))
  >>> bigcow = root._getOb("bigcow")

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

  We can even do some functional testing:
  >>> browser.open('http://localhost/cow/myview')
  >>> print browser.contents
  <html>
    <body>
      <div class="layout"><p> My nice Content </p></div>
    </body>
  </html>

  >>> browser.open('http://localhost/bigcow/myview')
  >>> print browser.contents
  <html>
    <body>
      <div class="layout"><p> My big cool Content </p>
      </div>
    </body>
  </html>


"""
from five import grok

from zope import interface
from five.megrok.layout import Layout, Page


class Cow(grok.Model):
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

