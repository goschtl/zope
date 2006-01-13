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

from zope.app import zapi
from zope.app.copypastemove.interfaces import IObjectMover, IObjectCopier
from zope.app.publication.http import MethodNotAllowed

from zope.app.traversing.api import traverse, getRoot
from zope.app.traversing.interfaces import TraversalError

from interfaces import IIfHeader

class COPY(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def COPY(self):
        #
        # get and verify data send in the HTTP request
        #
        depth = self.request.getHeader('depth', 'infinity')
        if depth not in ('0', 'infinity'):
            self.request.response.setStatus(400)
            return ''

        # can't copy method
        copier = IObjectCopier(self.context)
        if not copier.copyable():
            raise MethodNotAllowed(self.context, self.request)

        # find the destination
        dest = self.request.getHeader('destination', '')
        while dest and dest[-1] == '/':
            dest = dest[:-1]
        if not dest:
            self.request.response.setStatus(400)
            return ''

        # find the overwrite header
        overwrite = self.request.getHeader('overwrite', 't').lower().strip()
        if overwrite == 't':
            overwrite = True
        elif overwrite == 'f':
            overwrite = False
        else:
            self.request.response.setStatus(400)
            return ''

        # find destination if it exists and if it
        # dest is always treated has an absoluteURI has in rfc2396
        scheme, location, destpath, query, fragment = urlsplit(dest)
        try:
            destob = traverse(getRoot(self.context), destpath)
            exists = True
        except TraversalError:
            destob = None
            exists = False

        if destob is not None and not overwrite:
            self.request.response.setStatus(412)
            return ''
        elif destob is not None and destob is self.context:
            self.request.response.setStatus(403)
            return ''            
        elif destob is not None:
            ifparser = zapi.queryMultiAdapter((destob, self.request), IIfHeader)
            if ifparser is not None and not ifparser():
                self.request.response.setStatus(423)
                return ''

            # we need to delete this object
            parent = destob.__parent__
            del parent[destob.__name__]

        # check parent
        parentpath = destpath.split('/')
        destname   = parentpath.pop()
        try:
            parent = traverse(getRoot(self.context), parentpath)
        except TraversalError:
            parent = None
        if parent is None:
            self.request.response.setStatus(409)
            return ''

        if not copier.copyableTo(parent):
            self.request.response.setStatus(409)
            return ''

        copier.copyTo(parent, destname)

        self.request.response.setStatus(exists and 204 or 201)
        return ''
