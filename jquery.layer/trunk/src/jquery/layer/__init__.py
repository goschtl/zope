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
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""

from zope.publisher.interfaces.browser import IBrowserRequest


# JavaScript layers
class IXMLHTTPJavaScriptBrowserLayer(IBrowserRequest):
    """The XMLHTTP javascript layer."""


class IJSONJavaScriptBrowserLayer(IBrowserRequest):
    """The JSON javascript layer."""


class IJQueryJavaScriptBrowserLayer(IBrowserRequest):
    """The JQuery javascript layer."""


class IJQueryPackJavaScriptBrowserLayer(IBrowserRequest):
    """The JQuery javascript layer."""


# all-in-one layers
class IJQueryBrowserLayer(IXMLHTTPJavaScriptBrowserLayer, 
    IJSONJavaScriptBrowserLayer, IJQueryJavaScriptBrowserLayer):
    """The JQuery layer including xmlhttp and json libraries."""


class IJQueryPackBrowserLayer(IXMLHTTPJavaScriptBrowserLayer,
    IJSONJavaScriptBrowserLayer, IJQueryPackJavaScriptBrowserLayer):
    """The JQuery debug layer including xmlhttp and json libraries."""
