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
$Id: Widget.py,v 1.4 2002/10/28 23:52:31 jim Exp $
"""
from IWidget import IWidget
from Zope.Schema.Exceptions import ValidationError
from Zope.App.Forms.Exceptions import WidgetInputError

class Widget(object):
    """Mix-in class providing some functionality common accross view types
    """


    __implements__ = IWidget

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # See Zope.App.Forms.IWidget.IWidget
    propertyNames = []

    def getValue(self, name):
        'See Zope.App.Forms.IWidget.IWidget'
        if name in self.propertyNames:
            return getattr(self, name, None)

    def getName(self):
        return self.context.getName()

    def getTitle(self):
        return self.context.title

    def getData(self):
        raw = self._getRawData()
        value = self._convert(raw)
        try:
            self.context.validate(value)
        except ValidationError, v:
            raise WidgetInputError(self.getName(), self.getTitle(), v)

        return value

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
                  
class Customizer:
    """Objects for making shorthands for creating CustomWidgets
    """
    
    def __init__(self, widget_class):
        self.__widget_class = widget_class

    def __call__(self, **kw):
        # XXX should have error checking here!
        return CustomWidgets(self.__widget_class, **kw)
