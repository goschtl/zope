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
$Id: Widget.py,v 1.5 2002/11/11 20:52:57 jim Exp $
"""
from IWidget import IWidget
from Zope.Schema.Exceptions import ValidationError
from Zope.App.Forms.Exceptions import WidgetInputError
from Zope.ComponentArchitecture.IView import IViewFactory

class Widget(object):
    """Mix-in class providing some functionality common accross view types
    """


    __implements__ = IWidget

    _prefix = 'field.'
    _data = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.name = self._prefix + context.__name__

    # See Zope.App.Forms.IWidget.IWidget
    propertyNames = []

    def getValue(self, name):
        'See Zope.App.Forms.IWidget.IWidget'
        if name in self.propertyNames:
            return getattr(self, name, None)

    def setPrefix(self, prefix):
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__

    def setData(self, value):
        self._data = value

    def haveData(self):
        raise TypeError("haveData has not been implemented")

    def getData(self):
        raise TypeError("haveData has not been implemented")

    title = property(lambda self: self.context.title)

    required = property(lambda self: self.context.required)

class CustomWidget(object):
    """Custom Widget."""
    __implements__ = IViewFactory

    def __init__(self, widget, **kw):
        self.widget = widget
        self.kw = kw
        
    def __call__(self, context, request):
        instance = self.widget(context, request)
        for item in self.kw.items():
            setattr(instance, item[0], item[1])
        return instance
