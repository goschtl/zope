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
"""WebDAV method DELETE

Implementation of RFC 2518, Section 8.6

$Id$
"""
__docformat__ = "reStructuredText"
from zope.app import zapi


class DELETE(object):
    """Delete a Non-Collection Resource

    RFC 2518, Section 8.6.1 requires that we do not just delete the URI
    specified, but *any* reference of the resource in any collection or
    internal reference.
    """

    def DELETE(self):
        # XXX: Determine whether the resource is locked.
        locked = None
        if locked:
            request.response.setStatus(423)
            return

        # When we delete a resource (in Python terms 'object') at one place,
        # we leave it up to the Zope 3 framework to delete all its references.
        container = zapi.getParent(self.context)
        del container[zapi.name(self.context)]



class DELETECollection(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        # Make sure that the depth is always 'infinity' as required by the RFC
        depth = request.getHeader('Depth', 'infinity')
        if depth is not 'infinity':
            raise XXXError
