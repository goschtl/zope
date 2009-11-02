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
  [{'action': '',
    'description': '',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': [{'action': 'optionone',
                 'description': u'',
                 'extra': None,
                 'icon': None,
                 'selected': u'',
                 'submenu': None,
                 'title': 'Option one'}],
    'title': 'Options'},
   {'action': 'edit',
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
  [{'action': '',
    'description': '',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': [{'action': 'optionone',
                 'description': u'',
                 'extra': None,
                 'icon': None,
                 'selected': u'',
                 'submenu': None,
                 'title': 'Option one'}],
    'title': 'Options'},
   {'action': '',
    'description': '',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': [{'action': 'configoption',
                 'description': u'',
                 'extra': None,
                 'icon': None,
                 'selected': u'',
                 'submenu': None,
                 'title': 'Protected configuration'}],
    'title': 'Setup'},
   {'action': 'edit',
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
from grokcore.component import Context, name, title, description
from grokcore.view import View
from grokcore.security import Permission, require

import megrok.menu

from pprint import pformat
from zope.component import getUtility
from zope.app.publisher.interfaces.browser import IBrowserMenu

class Mammoth(Context):
    pass

class Actions(megrok.menu.Menu):
    name('actions')
    title('Actions')
    description('')

# You can either refer to the menu class itself:

class Index(View):
    title('View')
    megrok.menu.menuitem(Actions)

    def render(self):
        return 'index'

# or you can refer to its identifier:

class Edit(View):
    title('Edit')
    megrok.menu.menuitem('actions')

    def render(self):
        return 'edit'

# also you can define sub-menus items
class Options(megrok.menu.SubMenuItem):
    name('options')
    title('Options')
    description('')

    megrok.menu.menuitem('actions')

class OptionOne(View):
    title('Option one')
    megrok.menu.menuitem('options')

    def render(self):
        return 'option one'

# Here's a view that's protected by a permission. We expect the menu
# item that we configure for it to have the same permission setting:

class ManageStuff(Permission):
    name('my.ManageStuff')

class Manage(View):
    require(ManageStuff)
    title('Manage')
    megrok.menu.menuitem('actions')

    def render(self):
        return 'manage'

#Sub menus item are also available to be protected using a permission
class Setup(megrok.menu.SubMenuItem):
    require(ManageStuff)
    name('setup')
    title('Setup')
    description('')

    megrok.menu.menuitem('actions')

class ConfigOption(View):
    title('Protected configuration')
    megrok.menu.menuitem('setup')

    def render(self):
        return 'Configuration'

class ShowMenu(View):

    def render(self):
        menu = getUtility(IBrowserMenu, 'actions')
        return pformat(menu.getMenuItems(self.context, self.request))

def test_suite():
    from zope.testing import doctest
    from megrok.menu.tests import FunctionalLayer
    suite = doctest.DocTestSuite()
    suite.layer = FunctionalLayer
    return suite
