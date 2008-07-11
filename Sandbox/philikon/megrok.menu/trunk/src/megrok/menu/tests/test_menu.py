"""

  >>> from zope.component import getUtility
  >>> from zope.app.publisher.interfaces.browser import IBrowserMenu
  >>> from zope.publisher.browser import TestRequest

  >>> menu = getUtility(IBrowserMenu, 'tabs')
  >>> manfred = Mammoth()
  >>> request = TestRequest()

  >>> from pprint import pprint
  >>> pprint(menu.getMenuItems(manfred, request))
  [{'action': 'edit',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'Edit'},
   {'action': 'index',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'View'}]

"""
import grok
import megrok.menu

class Mammoth(grok.Model):
    pass

class Tabs(megrok.menu.Menu):
    grok.name('tabs')
    grok.title('Tabs')
    grok.description('')

class Index(grok.View):
    grok.title('View')
    megrok.menu.menuitem(Tabs)

    def render(self):
        return 'index'

class Edit(grok.View):
    grok.title('Edit')
    megrok.menu.menuitem('tabs')

    def render(self):
        return 'edit'


def test_suite():
    from zope.testing import doctest
    from megrok.menu.tests import FunctionalLayer
    suite = doctest.DocTestSuite()
    suite.layer = FunctionalLayer
    return suite
