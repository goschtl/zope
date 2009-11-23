"""
  Let's create a test content:
  >>> from five.megrok.layout.ftests.layout.pagesecurity import *
  >>> root = getRootFolder()
  >>> id = root._setObject("home", Home(id='home'))

  Now we can go on our page:
  >>> from Products.Five.testbrowser import Browser
  >>> browser = Browser()

  >>> browser.open('http://localhost/home/publicview')
  >>> print browser.contents
  <html>
    <body>
      <div class="layout"><p> I can express myself freely </p></div>
    </body>
  </html>

  >>> browser.open('http://localhost/home/securedview')
  Traceback (most recent call last):
    ...
  HTTPError: HTTP Error 401: Unauthorized

  And if you give the permission to anonymous people that should work
  after:

  >>> root.home.manage_permission('View management screens', ['Anonymous',])
  >>> browser.open('http://localhost/home/securedview')
  >>> print browser.contents
  <html>
    <body>
      <div class="layout"><p> My secret </p></div>
    </body>
  </html>

"""
from five import grok

from zope import interface
from five.megrok.layout import Layout, Page


class Home(grok.Model):
    pass


class Master(Layout):
    grok.name('master')
    grok.context(Home)


class PublicView(Page):
    grok.context(interface.Interface)
    grok.require('zope2.View')

    def render(self):
        return "<p> I can express myself freely </p>"


class SecuredView(Page):
    grok.context(interface.Interface)
    grok.require('zope2.ViewManagementScreens')

    def render(self):
        return "<p> My secret </p>"
