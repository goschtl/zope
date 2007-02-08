##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Filesystem synchronization functions.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope import interface
from zope import component
from zope.traversing.api import getPath
from zope.annotation.interfaces import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.fssync.server.syncer import Syncer
from zope.app.fssync.interfaces import IFSSyncFactory

from interfaces import IFSSyncAnnotations

def dottedname(klass):
    return "%s.%s" % (klass.__module__, klass.__name__)

class FSSyncAnnotations(AttributeAnnotations):
    """Default adapter for access to attribute annotations.
       Should be registered as trusted adapter.
    """
    interface.implements(IFSSyncAnnotations)


def provideSynchronizer(klass, factory):
    if klass is not None:
        name = dottedname(klass)
    else:
        name = ''
    component.provideUtility(factory, provides=IFSSyncFactory, name=name)
    

def getObjectId(obj):
    return getPath(obj)

def getSerializer(obj):
    """Returns a synchronizer.
    
    Looks for a named factory first and returns a default adapter
    if the dotted class name is not known.
    """
    name = dottedname(obj.__class__)
    factory = component.queryUtility(IFSSyncFactory, name=name)
    if factory is None:
        factory = component.getUtility(IFSSyncFactory)
    return factory(obj)

def getAnnotations(obj):
    return IFSSyncAnnotations(obj, None)


def toFS(obj, name, location):
    syncer = Syncer(getObjectId, getSerializer, getAnnotations)
    return syncer.toFS(obj, name, location)
