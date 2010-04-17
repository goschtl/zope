##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id: __init__.py 69386 2006-08-10 08:24:12Z rogerineichen $
"""

import zope.interface
import zope.component
from zope.publisher.browser import BrowserView, BrowserPage
from zope.security.interfaces import Unauthorized
from zope.exceptions.interfaces import UserError

from z3c.layer import minimal


class IMinimalTestingSkin(minimal.IMinimalBrowserLayer):
    """The IMinimalBrowserLayer testing skin."""


class TestingStandardMacros(BrowserView):

    zope.interface.implements(zope.interface.common.mapping.IItemMapping)

    macro_pages = ('page_macros', 'view_macros', 'error_macros')
    aliases = {
        'view': 'page',
        'dialog': 'page',
        'addingdialog': 'page'
        }

    def __getitem__(self, key):
        key = self.aliases.get(key, key)
        context = self.context
        request = self.request
        for name in self.macro_pages:
            page = zope.component.getMultiAdapter((context, request),
                name=name)
            try:
                v = page[key]
            except KeyError:
                pass
            else:
                return v
        raise KeyError(key)


class UnauthorizedPage(BrowserPage):
    """Unauthorized view."""

    def __call__(self):
        raise Unauthorized('not authorized')
        return u''


class UserErrorPage(BrowserPage):
    """Unauthorized view."""

    def __call__(self):
        raise UserError('simply user error')
        return u''


class SystemErrorPage(BrowserPage):
    """Unauthorized view."""

    def __call__(self):
        raise Exception('simply system error')
        return u''


class ContainerContentsPage(BrowserPage):
    """Contents of a conatiner."""

    def __call__(self):
        return str([type(x) for x in self.context.values()])

