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
"""WebDAV COPY method support

$Id$
"""
__docformat__ = 'restructuredtext'

from urlparse import urlsplit

from zope import component
from zope.app.copypastemove.interfaces import IObjectCopier, IObjectMover
from zope.app.publication.http import MethodNotAllowed

from zope.app.traversing.api import traverse, getRoot, getParent
from zope.app.traversing.interfaces import TraversalError

from interfaces import IIfHeader
from common import DAVError, DAVConflictError, ForbiddenError, \
     BadDAVRequestError, PreConditionFailedError, AlreadyLockedError


class Base(object):
    """Base class for copying and moving objects. Contains some helper
    methods shared between both methods implementations.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getDepth(self):
        depth = self.request.getHeader('depth', 'infinity')
        if depth not in ('0', 'infinity'):
            raise BadDAVRequestError, "invalid depth"
        return depth

    def getDestinationPath(self):
        # find the destination path
        dest = self.request.getHeader('destination', None)
        while dest and dest[-1] == '/':
            dest = dest[:-1]
        if not dest:
            raise BadDAVRequestError, "invalid destination header"

        scheme, location, destpath, query, fragment = urlsplit(dest)

        return destpath

    def getDestinationAndParentObject(self, default = None):
        # find destination if it exists and if it
        # dest is always treated has an absoluteURI has in rfc2396
        destpath = self.getDestinationPath()
        try:
            destob = traverse(getRoot(self.context), destpath)
        except TraversalError:
            destob = None

        overwrite = self.getOverwrite()

        parentpath = destpath.split('/')
        destname   = parentpath.pop()
        try:
            parent = traverse(getRoot(self.context), parentpath)
        except TraversalError:
            raise DAVConflictError(None, "failed to find destinations parent")

        if destob is not None and not overwrite:
            raise PreConditionFailedError(None,
                                          "can't overwrite destination object")
        elif destob is not None and destob is self.context:
            raise ForbiddenError(None, "objects are the same")
        elif destob is not None:
            ifparser = component.queryMultiAdapter((destob, self.request),
                                                   IIfHeader)
            if ifparser is not None and not ifparser():
                raise AlreadyLockedError(None,
                                         "destination object is already locked")

            # we need to delete this object
            parent = destob.__parent__
            del parent[destob.__name__]

        return destob, parent

    def getOverwrite(self):
        # find the overwrite header
        overwrite = self.request.getHeader('overwrite', 't').lower().strip()
        if overwrite == 't':
            overwrite = True
        elif overwrite == 'f':
            overwrite = False
        else:
            raise BadDAVRequestError, "invalid overwrite header"

        return overwrite


class COPY(Base):

    def handleCopy(self):
        # can't copy method
        copier = IObjectCopier(self.context)
        if not copier.copyable():
            raise MethodNotAllowed(self.context, self.request)

        # overwrite header
        overwrite = self.getOverwrite()

        # get the destination if it exists
        destob, parent = self.getDestinationAndParentObject()

        destname = self.getDestinationPath().split('/').pop()

        if not copier.copyableTo(parent, destname):
            self.request.response.setStatus(409)
            return ''

        copier.copyTo(parent, destname)

        self.request.response.setStatus(destob is not None and 204 or 201)
        return ''

    def COPY(self):
        try:
            return self.handleCopy()
        except DAVError, e:
            self.request.response.setStatus(e.status)
            return ''


class MOVE(Base):

    def handleMove(self):
        # can't copy method
        mover = IObjectMover(self.context)
        if not mover.moveable():
            raise MethodNotAllowed(self.context, self.request)

        # get the destination if it exists
        destob, parent = self.getDestinationAndParentObject()

        destname = self.getDestinationPath().split('/').pop()

        if not mover.moveableTo(parent, destname):
            self.request.response.setStatus(409)
            return ''

        mover.moveTo(parent, destname)

        self.request.response.setStatus(destob is not None and 204 or 201)
        return ''

    def MOVE(self):
        try:
            return self.handleMove()
        except DAVError, e:
            self.request.response.setStatus(e.status)
            return ''
