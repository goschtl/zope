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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: delete.py,v 1.3 2003/06/23 17:17:04 sidnei Exp $
"""
__metaclass__ = type

from zope.component import getAdapter
from zope.context import getWrapperContainer, getWrapperData
from zope.app.interfaces.file import IWriteDirectory
from zope.app.interfaces.container import IZopeWriteContainer

class DELETE:
    """Delete handler for all objects
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def DELETE(self):
        request = self.request

        victim = self.context
        container = getWrapperContainer(victim)
        name = getWrapperData(victim)['name']


        # Get a "directory" surrogate for the container
        dir = getAdapter(container, IWriteDirectory)

        # Get the zope adapter for that
        dir = getAdapter(dir, IZopeWriteContainer)

        # Now do the delete
        del dir[name]

        return ''


