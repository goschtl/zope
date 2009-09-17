##############################################################################
#
# Copyright (c) 2003-2009 Zope Corporation and Contributors.
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
"""Location copying/pickling support

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.component import adapts
from zope.copy.interfaces import ICopyHook, ResumeCopy
from zope.interface import implements

from zope.location.interfaces import ILocation, IRoot, ITraverser
from zope.location.location import inside
from zope.location.traversing import LocationPhysicallyLocatable


class LocationCopyHook(object):
    """Copy hook to preserve copying referenced objects that are not
    located inside object that's being copied.

    To see the problem, imagine we want to copy an ILocation object that
    contains an attribute-based reference to another ILocation object
    and the referenced object is not contained inside object being copied. 
    
    Without this hook, the referenced object will be cloned:
    
    >>> from zope.location.location import Location, locate
    >>> root = Location()
    >>> page = Location()
    >>> locate(page, root, 'page')
    >>> image = Location()
    >>> locate(page, root, 'image')
    >>> page.thumbnail = image
    
    >>> from zope.copy import copy
    >>> page_copy = copy(page)
    >>> page_copy.thumbnail is image
    False

    But if we will provide a hook, the attribute will point to the
    original object as we might want.

    >>> from zope.component import provideAdapter
    >>> provideAdapter(LocationCopyHook)

    >>> from zope.copy import copy
    >>> page_copy = copy(page)
    >>> page_copy.thumbnail is image
    True
    
    """
    
    adapts(ILocation)
    implements(ICopyHook)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, toplevel, register):
        if not inside(self.context, toplevel):
            return self.context
        raise ResumeCopy

# BBB 2009/02/09
# The locationCopy was replaced by more generic "clone" function
# in the zope.copy package. This reference may be removed someday.
from zope.copy import clone as locationCopy

# BBB 2009/02/09
# The CopyPersistent was made more generic and moved to the
# zope.copy package. This reference may be removed someday.
from zope.copy import CopyPersistent
