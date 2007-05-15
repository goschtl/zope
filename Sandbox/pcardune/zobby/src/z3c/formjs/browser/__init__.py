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
$Id: __init__.py 217 2007-04-15 20:25:48Z rineichen $
"""
__docformat__ = "reStructuredText"

from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import JavaScriptViewlet

class IFormJSJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


FormJSJavaScriptViewlet = JavaScriptViewlet('z3c.formjs/formjs.js')
