##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Broken-object support

$Id: broken.py,v 1.2 2004/03/02 17:51:49 philikon Exp $
"""


import ZODB.broken
import zope.interface
import zope.app.location.interfaces
import zope.app.event.function

class IBroken(zope.interface.Interface):
    """Marker interface for broken objects
    """

class Broken(ZODB.broken.Broken):
    zope.interface.implements(IBroken, zope.app.location.interfaces.ILocation)

    def __parent__(self):
        return self.__Broken_state__.get('__parent__')

    __parent__ = property(__parent__)

    def __name__(self):
        return self.__Broken_state__.get('__name__')
    
    __name__ = property(__name__)

def installBroken(event):
    
    Broken_ = Broken # make it local for speed
    find_global = ZODB.broken.find_global
    
    def classFactory(connection, modulename, globalname):
        return find_global(modulename, globalname, Broken_)

    event.database.setClassFactory(classFactory)

installBroken = zope.app.event.function.Subscriber(installBroken)
