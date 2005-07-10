##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test browser menus

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_menu():
    """
    Test menus

    Before we can start we need to set up a few things.  For menu
    configuration, we have to start a new interaction:

      >>> from Products.Five.traversable import newInteraction
      >>> newInteraction()

      >>> import Products.Five.browser.tests
      >>> from Products.Five import zcml
      >>> zcml.load_config('menu.zcml', package=Products.Five.browser.tests) 

    Now for some actual testing... Let's look up the menu we registered:

      >>> from Products.Five.traversable import FakeRequest
      >>> from zope.app.publisher.browser.globalbrowsermenuservice import \\
      ...     globalBrowserMenuService

      >>> request = FakeRequest()
      >>> request.getURL = lambda: 'http://www.infrae.com'
      >>> menu = globalBrowserMenuService.getMenu(
      ...     'testmenu', self.folder, request)

    It should have 

      >>> len(menu)
      4

    Sort menu items by title so we get a stable testable result:

      >>> menu.sort(lambda x, y: cmp(x['title'], y['title']))
      >>> from pprint import pprint
      >>> pprint(menu)
      [{'action': '@@cockatiel_menu_public.html',
        'description': '',
        'extra': None,
        'selected': '',
        'title': u'Page in a menu (public)'},
       {'action': u'seagull.html',
        'description': u'This is a test menu item',
        'extra': None,
        'selected': '',
        'title': u'Test Menu Item'},
       {'action': u'parakeet.html',
        'description': u'This is a test menu item',
        'extra': None,
        'selected': '',
        'title': u'Test Menu Item 2'},
       {'action': u'falcon.html',
        'description': u'This is a test menu item',
        'extra': None,
        'selected': '',
        'title': u'Test Menu Item 3'}]

    Let's create a manager user account and log in.  We should get the
    protected menu items now:

      >>> uf = self.folder.acl_users
      >>> uf._doAddUser('manager', 'r00t', ['Manager'], [])
      >>> self.login('manager')
      >>> newInteraction()

      >>> menu = globalBrowserMenuService.getMenu(
      ...     'testmenu', self.folder, request)


    XXX This should really yield 7 menu items here (4 public ones + 3
    protected ones).  The problem is this: GlobalBrowserMenuService
    uses zope.security.management.checkPermission to see whether we're
    qualified to see a menu item.  That function uses the
    interaction's checkPermission method.  We thought that we could
    register getSecurityManager() as an interaction, but that expects
    a Zope 2 permission name whereas GlobalBrowserMenuService sends a
    Zope 3 permission id.

    TODO possible fix: register menu items with the permission title,
    not permission id.  Another, probably more thorough option:
    decorate getSecurityManager()'s checkPermission method with one
    that does the conversion between zope 3 permission id and zope 2
    permission title.

      >>> len(menu)
      4
    """

def test_suite():
    from Testing.ZopeTestCase import installProduct, ZopeDocTestSuite
    installProduct('Five')
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
