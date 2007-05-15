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
$Id: __init__.py 69386 2006-08-10 08:24:12Z rogerineichen $
"""

from z3c.formjs.interfaces import IFormJSLayer
from z3c.layer.pagelet import IPageletBrowserLayer


class IDemoBrowserLayer(IFormJSLayer, IPageletBrowserLayer):
    """Demo browser layer using formjs layer."""
