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
from zope import xmlpickle
from zope.traversing.api import getPath
from zope.annotation.interfaces import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.proxy import removeAllProxies
from zope.security.management import checkPermission
from zope.security.checker import ProxyFactory

from zope.fssync.server.syncer import Syncer
from zope.fssync.server import entryadapter
from zope.app.fssync.interfaces import IFSSyncFactory

import interfaces
import fspickle

def dottedname(klass):
    return "%s.%s" % (klass.__module__, klass.__name__)


class LocationAwareDefaultFileAdapter(entryadapter.DefaultFileAdapter):
    """A specialization of the DefaultFileAdapter which uses a location aware
    pickle.
    """
    
    def getBody(self):
        return xmlpickle.toxml(fspickle.dumps(self.context))
    
    
class FSSyncAnnotations(AttributeAnnotations):
    """Default adapter for access to attribute annotations.
       Should be registered as trusted adapter.
    """
    interface.implements(interfaces.IFSSyncAnnotations)


def provideSynchronizer(klass, factory):
    if klass is not None:
        name = dottedname(klass)
    else:
        name = ''
    component.provideUtility(factory, provides=interfaces.IFSSyncFactory, name=name)
    

def getObjectId(obj):
    return getPath(obj)

def getSerializer(obj):
    """Returns a synchronizer.
    
    Looks for a named factory first and returns a default adapter
    if the dotted class name is not known.
    
    Checks also for the permission to call the factory in the context of the given object.
    Removes the security proxy if a call is allowed.
    """
    name = dottedname(obj.__class__)
    factory = component.queryUtility(interfaces.IFSSyncFactory, name=name)
    if factory is None:
        factory = component.queryUtility(interfaces.IFSSyncFactory)

    checker = getattr(factory, '__Security_checker__', None)
    if checker is None:
        return factory(obj)
        
    permission = checker.get_permissions['__call__']
    if checkPermission(permission, obj):
        return ProxyFactory(factory(removeAllProxies(obj)))
        
    return None

def getAnnotations(obj):
    return interfaces.IFSSyncAnnotations(obj, None)


def toFS(obj, name, location):
    syncer = Syncer(getObjectId, getSerializer, getAnnotations)
    return syncer.toFS(obj, name, location)
