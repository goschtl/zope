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

This file defines what layer make up the z3c.boston skin.

$Id$
"""

import zope.app.boston
import z3c.layer.pagelet
import z3c.form.interfaces
import z3c.formui.interfaces
from jquery.layer import IJQueryJavaScriptBrowserLayer    # required for formjs

class IPageletLayer(z3c.form.interfaces.IFormLayer,
                    IJQueryJavaScriptBrowserLayer,
                    z3c.layer.pagelet.IPageletBrowserLayer):
    pass


class Boston(zope.app.boston.Boston,
            z3c.formui.interfaces.IDivFormLayer,          # this is arbitrary - could also
                                                          # use the table layer
            IPageletLayer):
    pass
