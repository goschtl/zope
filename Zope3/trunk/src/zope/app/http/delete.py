##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""HTTP DELETE verb

$Id: delete.py,v 1.6 2004/03/15 13:10:51 srichter Exp $
"""
__metaclass__ = type

from zope.app.filerepresentation.interfaces import IWriteDirectory

class DELETE:
    """Delete handler for all objects
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def DELETE(self):
        request = self.request

        victim = self.context
        container = victim.__parent__
        name = victim.__name__


        # Get a "directory" surrogate for the container
        dir = IWriteDirectory(container)

        del dir[name]

        return ''


