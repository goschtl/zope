"""
  >>> from zope.component import getUtility
  >>> from zope.app.publisher.interfaces.browser import IBrowserMenu
  >>> from zope.publisher.browser import TestRequest

A menu is available as a named utility providing ``IBrowserMenu``.

  >>> menu = getUtility(IBrowserMenu, 'tabs')
  >>> manfred = Mammoth()
  >>> request = TestRequest()

In order to retrieve the menu items, we need to pass in a context
object and a request.  The menu then determines which menu items are
available for this particular object and the principal that's attached
to the request:

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

from grokcore.component import Context, name, title, description
from grokcore.view import View
from grokcore.security import Permission, require
import megrok.menu

class Mammoth(Context):
    pass

class Tabs(megrok.menu.Menu):
    name('tabs')
    title('Tabs')
    description('')

# You can either refer to the menu class itself:

class Index(View):
    title('View')
    megrok.menu.menuitem(Tabs)

    def render(self):
        return 'index'

# or you can refer to its identifier:

class Edit(View):
    title('Edit')
    megrok.menu.menuitem('tabs')

    def render(self):
        return 'edit'


def test_suite():
    from zope.testing import doctest
    from megrok.menu.tests import FunctionalLayer
    suite = doctest.DocTestSuite()
    suite.layer = FunctionalLayer
    return suite
