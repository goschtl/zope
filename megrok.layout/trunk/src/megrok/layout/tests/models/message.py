"""
  >>> from megrok.layout import ILayout
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest

  >>> kitty = Cat()
  >>> request = TestRequest()
  >>> mylayout = getMultiAdapter((request, kitty), ILayout)
  >>> myview = getMultiAdapter((kitty, request), name='utils')

  >>> print myview.flash(u'test')
  None

  >>> from zope.security.management import newInteraction
  >>> newInteraction(request)

  >>> grok.testing.grok('megrok.layout.messages')
  >>> print myview.flash(u'test')
  True

  >>> from zope.component import getUtility
  >>> from z3c.flashmessage.interfaces import IMessageReceiver
  >>> receiver = getUtility(IMessageReceiver)
  >>> messages = [i for i in receiver.receive()]
  >>> messages
  [<z3c.flashmessage.message.Message object at ...>]

  >>> print ", ".join([msg.message for msg in messages])
  test

  >>> from zope.security.management import endInteraction
  >>> endInteraction()

"""
import grokcore.component as grok
from grokcore.view import templatedir
from zope.interface import Interface
from megrok.layout import Layout, Page

templatedir('templates')


class Cat(grok.Context):
    pass


class Master(Layout):
    grok.name('master')
    grok.context(Cat)


class Utils(Page):
    grok.context(Interface)

    def render(self):
        return "<p>A purring cat</p>"
