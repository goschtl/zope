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
"""Marker interfaces required to configure a skin.

This file defines what layer make up the z3c.rotterdam skin.

$Id$
"""

import zope.app.rotterdam
import z3c.layer.pagelet
import z3c.form.interfaces
import z3c.formui.interfaces
import z3c.formjs.interfaces
from zope.viewlet.interfaces import IViewletManager
from jquery.layer import IJQueryJavaScriptBrowserLayer    # required for formjs

class IPageletLayer(z3c.form.interfaces.IFormLayer,
                    IJQueryJavaScriptBrowserLayer,
                    z3c.layer.pagelet.IPageletBrowserLayer):
    pass


class Rotterdam(zope.app.rotterdam.Rotterdam,
                z3c.formui.interfaces.IDivFormLayer,          # this is arbitrary - could also
                                                              # use the table layer
                IPageletLayer):
    pass

class ICSS(z3c.formui.interfaces.ICSS):
    """CSS viewlet manager."""

class IJavaScript(
        IViewletManager,
        IJQueryJavaScriptBrowserLayer,
        z3c.formjs.interfaces.IDynamicJavaScript):
    """JavaScript viewlet manager."""
