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
$Id: Widget.py,v 1.2 2002/07/16 23:42:58 srichter Exp $
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


class CustomWidget(object):
    """Custom Widget."""
    __instance_implements__ = IWidget

    def __init__(self, widget, **kw):
        self.widget = widget
        self.kw = kw
        
    def __call__(self, context, request):
        instance = self.widget(context, request)
        for item in self.kw.items():
            setattr(instance, item[0], item[1])
        return instance
                  
