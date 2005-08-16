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
"""Pagelet Demo

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent

from zope.interface import implements

from zope.app.container.contained import Contained

from zope.app.demo.pagelet.interfaces import IPageletContent



class PageletContent(Persistent, Contained):
    """A sample content type just for to test pagelet."""

    implements(IPageletContent)

    __parent__ = __name__ = None
    
    _title = u''
    _description = u''
    
    def getTitle(self):
        """Get the title of the object."""
        return self._title

    def setTitle(self, title):
        """Set the title of the object."""
        self._title = title

    title = property(getTitle, setTitle)

    def getDescription(self):
        """Get the description of the object."""
        return self._description

    def setDescription(self, description):
        """Set the description of the object."""
        self._description = description

    description = property(getDescription, setDescription)
