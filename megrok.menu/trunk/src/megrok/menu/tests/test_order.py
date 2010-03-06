"""
  >>> from zope.component import getUtility
  >>> from zope.browsermenu.interfaces import IBrowserMenu
  >>> from zope.publisher.browser import TestRequest

We log as anonymous::

  >>> newInteraction(Participation(Principal('zope.anybody')))

A menu is available as a named utility providing ``IBrowserMenu``.

  >>> menu = getUtility(IBrowserMenu, 'ordered')
  >>> manfred = Mammoth()
  >>> request = TestRequest()

In order to retrieve the menu items, we need to pass in a context
object and a request.  The menu then determines which menu items are
available for this particular object and the principal that's attached
to the request:

  >>> from pprint import pprint
  >>> pprint(menu.getMenuItems(manfred, request))
  [{'action': 'cluelessview',
    'description': "We keep the 'menuitem' directive order info if present !",
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'What should I chose ?'},
   {'action': 'firstview',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'my first view'},
   {'action': 'secondview',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'my second view'},
   {'action': 'thirdview',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'my third view'}]

   >>> endInteraction()

"""
import megrok.menu
import grokcore.viewlet as grok
from zope.security.management import newInteraction, endInteraction
from zope.security.testing import Principal, Participation


class Mammoth(grok.Context):
    pass


class OrderedMenu(megrok.menu.Menu):
    grok.name('ordered')
    grok.title('My menu')


class SecondView(grok.View):
    grok.order(2)
    grok.title('my second view')
    megrok.menu.menuitem('ordered')

    def render(self):
        return 'test'


class ThirdView(grok.View):
    grok.title('my third view')
    megrok.menu.menuitem('ordered', order=3)

    def render(self):
        return 'test'


class FirstView(grok.View):
    grok.order(1)
    grok.title('my first view')
    megrok.menu.menuitem('ordered')

    def render(self):
        return 'test'


class CluelessView(grok.View):
    grok.order(5)
    grok.title('What should I chose ?')
    grok.description("We keep the 'menuitem' directive "
                     "order info if present !")
    megrok.menu.menuitem('ordered', order=0)

    def render(self):
        return 'test'
    

def test_suite():
    from zope.testing import doctest
    suite = doctest.DocTestSuite()
    suite.layer = megrok.menu.tests.MegrokMenuLayer(megrok.menu.tests)
    return suite
