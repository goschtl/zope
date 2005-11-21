##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Tutorial Manager Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.app.apidoc import utilities
from zope.app import location
from zope.app import zapi

from zope.tutorial import interfaces


class TutorialManager(utilities.ReadContainerBase):
    """TutorialManager"""
    zope.interface.implements(interfaces.ITutorialManager,
                              location.interfaces.ILocation)

    def __init__(self, parent=None):
        self.__parent__ = parent
        self.__name__ = '++tutorials++'

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer"""
        utility = zapi.queryUtility(interfaces.ITutorial, key, default)
        if utility != default:
            utility = location.LocationProxy(utility, self, key)
        return utility

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""
        items = list(zapi.getUtilitiesFor(interfaces.ITutorial))
        items.sort()
        return [(name, location.LocationProxy(tutorial, self, name))
                for name, tutorial in items]


class tutorialsNamespace(object):
    """Used to traverse the `++tutorials++` namespace"""

    def __init__(self, ob=None, request=None):
        self.tutorialManager = TutorialManager(ob)

    def traverse(self, name, ignore=None):
        if name == '':
            return self.tutorialManager
        else:
            return self.tutorialManager[name]
