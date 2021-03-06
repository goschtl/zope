##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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

from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.pagelet import browser
import zam.api.layer


class IZAMTestPluginLayer(IBrowserRequest):
    """test plugin layer."""


class IZAMTestBrowserSkin(zam.api.layer.IZAMBrowserLayer, IZAMTestPluginLayer):
    """The ``ZAMTest`` browser skin including test plugin layer."""


class TestPage(browser.BrowserPagelet):
    """Test page."""


class PluginTestPage(browser.BrowserPagelet):
    """Plugin test page."""
