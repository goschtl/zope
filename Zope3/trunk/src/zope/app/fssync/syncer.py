##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Filesystem synchronization functions.

$Id: syncer.py,v 1.34 2004/03/06 17:48:49 jim Exp $
"""

from zope.component import getService
from zope.fssync.server.syncer import Syncer

from zope.app.interfaces.annotation import IAnnotations
from zope.app.traversing import getPath


def getObjectId(obj):
    return str(getPath(obj))

def getSerializer(obj):
    syncService = getService(obj, 'FSRegistryService')
    return syncService.getSynchronizer(obj)

def getAnnotations(obj):
    return IAnnotations(obj, None)


def toFS(obj, name, location):
    syncer = Syncer(getObjectId, getSerializer, getAnnotations)
    return syncer.toFS(obj, name, location)
