##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""
$Id: Widget.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from IWidget import IWidget

class Widget(object):
    """I do not know what will be in this class, but it provides an extra
    layer."""
    __implements__ = IWidget

    # See Zope.App.Forms.IWidget.IWidget
    propertyNames = []

    def getValue(self, name):
        'See Zope.App.Forms.IWidget.IWidget'
        if name in self.propertyNames:
            return getattr(self, name, None)
