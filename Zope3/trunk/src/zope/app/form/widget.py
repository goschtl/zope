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
$Id: widget.py,v 1.4 2003/01/09 14:13:08 jim Exp $
"""
from zope.app.interfaces.form import IWidget
from zope.component.interfaces import IViewFactory

__metaclass__ = type

class Widget:
    """Mix-in class providing some functionality common accross view types
    """
    __implements__ = IWidget

    _prefix = 'field.'
    _data = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.name = self._prefix + context.__name__

    # See IWidget
    propertyNames = []

    def getValue(self, name):
        'See IWidget'
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
        raise TypeError("getData has not been implemented")

    title = property(lambda self: self.context.title)

    required = property(lambda self: self.context.required)

class CustomWidget:
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
