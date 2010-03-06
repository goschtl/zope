"""
We log as anonymous::

  >>> newInteraction(Participation(Principal('zope.anybody')))

A menu is available as a named utility providing ``IBrowserMenu``.

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.browsermenu.interfaces import IBrowserMenu
  >>> from zope.component import getUtility

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

  >>> endInteraction()

"""

import megrok.menu
from grokcore.component import Context, name, title, description
from grokcore.security import Permission, require
from grokcore.view import View
from zope.security.management import newInteraction, endInteraction
from zope.security.testing import Principal, Participation


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
    suite = doctest.DocTestSuite()
    suite.layer = megrok.menu.tests.MegrokMenuLayer(megrok.menu.tests)
    return suite
