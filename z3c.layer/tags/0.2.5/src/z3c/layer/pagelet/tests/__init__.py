##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""

import zope.interface
import zope.component
from zope.publisher.browser import BrowserPage
from zope.security.interfaces import Unauthorized
from zope.exceptions.interfaces import UserError

from z3c.pagelet import browser
import z3c.layer.pagelet


class IPageletBrowserTestSkin(z3c.layer.pagelet.IPageletBrowserLayer):
    """The IJSABrowser testing skin."""


class TestPage(browser.BrowserPagelet):
    """Test page."""


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
    """Contents of a container."""

    def __call__(self):
        return str([type(x) for x in self.context.values()])

