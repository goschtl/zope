"""
Let's create a Mammoth object in the root folder so we can access
views through the publisher:

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> root['manfred'] = Mammoth()

As an anonymous user, we only see the unprotected menu items:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser('http://localhost/manfred/showmenu')
  >>> print browser.contents
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

After logging in as a manager, we also see the protected one:

  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.open('http://localhost/manfred/showmenu')
  >>> print browser.contents
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
    'title': 'View'},
   {'action': 'manage',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'Manage'}]

"""
import grok
import megrok.menu
from pprint import pformat
from zope.component import getUtility
from zope.app.publisher.interfaces.browser import IBrowserMenu

class Mammoth(grok.Model):
    pass

class Actions(megrok.menu.Menu):
    grok.name('actions')
    grok.title('Actions')
    grok.description('')

# You can either refer to the menu class itself:

class Index(grok.View):
    grok.title('View')
    megrok.menu.menuitem(Actions)

    def render(self):
        return 'index'

# or you can refer to its identifier:

class Edit(grok.View):
    grok.title('Edit')
    megrok.menu.menuitem('actions')

    def render(self):
        return 'edit'

# Here's a view that's protected by a permission. We expect the menu
# item that we configure for it to have the same permission setting:

class ManageStuff(grok.Permission):
    grok.name('my.ManageStuff')

class Manage(grok.View):
    grok.require(ManageStuff)
    grok.title('Manage')
    megrok.menu.menuitem('actions')

    def render(self):
        return 'manage'

class ShowMenu(grok.View):

    def render(self):
        menu = getUtility(IBrowserMenu, 'actions')
        return pformat(menu.getMenuItems(self.context, self.request))

def test_suite():
    from zope.testing import doctest
    from megrok.menu.tests import FunctionalLayer
    suite = doctest.DocTestSuite()
    suite.layer = FunctionalLayer
    return suite
