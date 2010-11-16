# -*- coding: UTF-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 Zope Foundation and Contributors.
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

from wax import *
from z3c.zodbbrowser.registry import getObjectPlugin


class oneProperty(object):
    u"""Data holder for one object property"""

    text = ''
    type = None
    expandable = False
    data = None

    def __init__(self, **kw):
        self.__dict__.update(kw)


class dataCollector(object):
    u"""Data holder for object properties.

    Kind of property bag.

    """
    def __init__(self):
        self._data=[]

    def add(self, text='', property=None):
        u"""add one property of an object
        the property will be inspected if it's expandable
        """
        plg = getObjectPlugin(text, property)
        expandable = plg.getExpandable()
        type = plg.getType()

        self.addLL(oneProperty(text = text,
                    expandable = expandable,
                    data=property,
                    type=type))

    def addLL(self, obj):
        u"""add one property of an object
        no inspection done, just appended to the list
        """
        self._data.append(obj)

    def getAll(self):
        u"""get all property data
        """
        return self._data


class BaseObjectPlugin(object):
    u"""Plugin base for object inspection"""

    def __init__(self, context):
        self.context = context

    def match(self, title):
        u"""return True if the context object can
        be handled by the current plugin
        """
        return False

    def getChildren(self):
        u"""Get child objects of the context object
        """
        return dataCollector()

    def getProps(self):
        u"""Get properties of the context object
        """
        return dataCollector()

    def getExpandable(self):
        u"""Return if the object is expandable, has child somethings
        """
        return False

    def getType(self):
        u"""return a type identifying the context object
        """
        return ''


class BaseSourcePlugin(object):
    u"""Plugin base for data source
    """
    def __init__(self, mainframe):
        self.mainframe = mainframe

    def open(self, parent):
        u"""open data source
        the user should select what to open e.g. with a dialog
        """
        pass

    def close(self):
        u"""close the opened data source
        """
        pass

    def getSupportedDisplays(self):
        u"""Get preferred/supported display modes of the data source.

        These will be looked up in the db_display registry for plugins.

        """
        return []

    def getDataForDisplay(self, mode):
        u"""Get the data to be displayed

        Called by the display plugin.

        (By the nature of the ZODB this is usually the root object)

        """
        return None

    def getTitle(self):
        u"""Return a user-readable title for the display window"""
        return ""


class BaseDisplayPlugin(MDIChildFrame):
    u"""Plugin base for data source display
    """

    #window and plugin title
    title = u''

    #def __init__(self, opener):
    #gets the data source passed
    #    pass


class BaseObjDisplayPlugin(object):
    u"""Plugin base for object display, used for right-click
    """

    #shortcut menu title
    title = u''

    def __init__(self, context, form):
        self.context = context
        self.form = form

    def getTitle(self):
        u"""get the text that should be displayed on the context menu
        """
        return self.title

    def onClick(self):
        u"""start processing
        """
        pass
