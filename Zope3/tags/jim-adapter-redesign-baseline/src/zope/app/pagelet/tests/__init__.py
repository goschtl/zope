##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pagelet tests

$Id$
"""
__docformat__ = 'restructuredtext'

import sys
from zope.interface import Interface, implements

from zope.security.checker import NamesChecker

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.app.pagelet.interfaces import IPageletSlot
from zope.app.pagelet.interfaces import IPagelet
from zope.app.pagelet.interfaces import IPageData



class ITestSlot(IPageletSlot):
    """Pagelet test slot."""


class TestSlot(object):
    """Test pagelet slot"""

    implements(ITestSlot)


class TestPagelet(object):
    """Test pagelet"""

    implements(IPagelet)

    frame = sys._getframe(1).f_globals
    _template = ViewPageTemplateFile('testfiles/test_pagelet.pt', frame)
    _weight = 0

    def __init__(self, context, request, view, ignored):
        self.context = context
        self.request = request
        self.view = view

    def __getitem__(self, name):
        """Get the macro by name."""
        return self._template.macros[name]

    def _getWeight (self):
        """The weight of the pagelet."""
        return self._weight

    weight = property(_getWeight)


class TestContext(object):
    """Test context"""

    implements(Interface)


class TestClass(object):
    """Test class"""

    implements(IPageData)
 
    def __init__(self, context, request, view):
        pass
        
    def getString(self):
        return "A demo string."


testChecker = NamesChecker(['__getitem__', '__call__', 'weight'])
