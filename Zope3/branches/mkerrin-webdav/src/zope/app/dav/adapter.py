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
"""WebDAV-related Adapters

$Id$
"""
__docformat__ = 'restructuredtext'

from xml.dom import minidom

from zope.interface import Interface, implements

from zope.app import zapi
from zope.app.dav.interfaces import IDAVSchema, IDAVActiveLock, IDAVLockEntry
from zope.app.dublincore.interfaces import IDCTimes
from zope.app.filerepresentation.interfaces import IReadDirectory
from zope.app.size.interfaces import ISized
from zope.app.file.interfaces import IFile
from zope.app.locking.interfaces import ILockable


class DAVSchemaAdapter(object):
    """An adapter for all content objects that provides the basic DAV
    schema/namespace."""
    implements(IDAVSchema)

    def __init__(self, object):
        self.context = object

    def displayname(self):
        value = zapi.name(self.context)
        if IReadDirectory(self.context, None) is not None:
            value = value + '/'
        return value
    displayname = property(displayname)

    def creationdate(self):
        dc = IDCTimes(self.context, None)
        if dc is None or dc.created is None:
            return None
        return dc.created
    creationdate = property(creationdate)

    def resourcetype(self):
        value = IReadDirectory(self.context, None)
        if value is not None:
            return [u'collection']
        return None
    resourcetype = property(resourcetype)

    def getcontentlanguage(self):
        return None
    getcontentlanguage = property(getcontentlanguage)

    def getcontentlength(self):
        sized = ISized(self.context, None)
        if sized is None:
            return None
        units, size = sized.sizeForSorting()
        if units == 'byte':
            return size
        return None
    getcontentlength = property(getcontentlength)

    def executable(self):
        return None
    executable = property(executable)

    def getcontenttype(self):
        file = IFile(self.context, None)
        if file is not None:
            return file.contentType.decode('utf-8')
        return None
    getcontenttype = property(getcontenttype)

    getetag = None

    def getlastmodified(self):
        dc = IDCTimes(self.context, None)
        if dc is None or dc.created is None:
            return None
        return dc.modified
    getlastmodified = property(getlastmodified)

    def supportedlock(self):
        return IDAVLockEntry(self.context, None)
    supportedlock = property(supportedlock)

    def lockdiscovery(self):
        lockable = ILockable(self.context, None)
        if lockable is None or not lockable.locked():
            return None
        return IDAVActiveLock(self.context, None)
    lockdiscovery = property(lockdiscovery)

    source = None


class LockEntry(object):
    implements(IDAVLockEntry)

    def __init__(self, context):
        pass

    lockscope = [u'exclusive']

    locktype = [u'write']


class ActiveLock(object):
    """represent a locked object that is the context of this adapter should
    be locked otherwise a TypeError is raised
    """
    implements(IDAVActiveLock)

    def __init__(self, context):
        self.context = context
        lockable = ILockable(self.context)
        if not lockable.locked():
            raise TypeError, "There are no active locks for this object"
        self.lockinfo = lockable.getLockInfo()

    def locktype_get(self):
        return self.lockinfo.get('locktype', None)
    def locktype_set(self, value):
        if len(value) != 1 or value[0] != u'write':
            raise ValueError, "invalid lock type"
        self.lockinfo['locktype'] = value
    locktype = property(locktype_get, locktype_set)

    def lockscope_get(self):
        return self.lockinfo.get('lockscope', None)
    def lockscope_set(self, value):
        if len(value) != 1 or value[0] != u'exclusive':
            raise ValueError, "unsupport lock scope value"
        self.lockinfo['lockscope'] = value
    lockscope = property(lockscope_get, lockscope_set)

    def depth_get(self):
        return u'0'
    def depth_set(self, value):
        self.lockinfo['depth'] = value
    depth = property(depth_get, depth_set)

    def owner_get(self):
        return self.lockinfo.get('owner', None)
    def owner_set(self, value):
        self.lockinfo['owner'] = value
    owner = property(owner_get, owner_set)

    def timeout_get(self):
        return u'Second-%d' % self.lockinfo.timeout
    timeout = property(timeout_get)

    def locktoken_get(self):
        return self.lockinfo['locktoken']
    locktoken = property(locktoken_get)
