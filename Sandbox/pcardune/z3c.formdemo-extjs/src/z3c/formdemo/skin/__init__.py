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
$Id$
"""
__docformat__ = "reStructuredText"

from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import CSSViewlet
from z3c.pagelet import browser
from z3c.formui import interfaces
from z3c.formdemo import layer

from z3c.formextjs.interfaces import IExtJSFormLayer, IJavaScript
from z3c.formextjs.interfaces import ICSS as IFormExtCSS

class IDivDemoBrowserSkin(interfaces.IDivFormLayer,
                          layer.IDemoBrowserLayer):
    """The ``Z3CFormDemo`` browser skin."""

class ITableDemoBrowserSkin(interfaces.ITableFormLayer,
                            layer.IDemoBrowserLayer):
    """The ``Z3CTableFormDemo`` browser skin."""

class IExtJSDemoBrowserSkin(IExtJSFormLayer,
                            layer.IDemoBrowserLayer):
    """The ``Z3CExtJSFormDemo`` browser skin."""

class ICSS(interfaces.ICSS, IFormExtCSS):
    """CSS viewlet manager."""

class IJavaScript(IJavaScript):
    """JavaScript viewlet manager."""


DemoCSSViewlet = CSSViewlet('demo.css')

