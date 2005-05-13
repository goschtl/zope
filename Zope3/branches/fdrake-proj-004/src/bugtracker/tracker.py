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
"""A Bug Tracker implementation

$Id$
"""
import re
from persistent import Persistent

from zope.interface import implements

from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import INameChooser

from bugtracker.interfaces import IBugTracker
from bugtracker.interfaces import IBugContainer


class BugTracker(BTreeContainer):
    """A BTree-based IBugTracker implementation.

    Internally bugs are identified as integer ids. Unfortunately, the
    IContainer interface expects ids to be strings, so we convert the integers
    to strings for this purpose. This is also the reason we do not use
    BTreeContainer, since it uses OOBTree, but we can use IOBTree now.
    """
    implements(IBugContainer, IBugTracker)

    def setTitle(self, title):
        """See zopeproducts.bugtracker.interfaces.IBugTracker"""
        dc = IZopeDublinCore(self)
        dc.title = title

    def getTitle(self):
        """See zopeproducts.bugtracker.interfaces.IBugTracker"""
        dc = IZopeDublinCore(self)
        return dc.title

    # See zopeproducts.bugtracker.interfaces.IBugTracker
    title = property(getTitle, setTitle)


int_re = re.compile('^[0-9]*$')
    
class BugTrackerNameChooser:
    """An adapter to choose names for bugs."""

    implements(INameChooser)
    __used_for__ = IBugTracker

    def __init__(self, context):
        self.context = context

    def chooseName(self, name, message):
        # It is sometimes necessary to force in a name, since bugs might refer
        # to each other. This is particularly important when importing XML
        # data.
        if isinstance(name, (str, unicode)) and name.startswith('bug'):
            name = name[3:]
        else:
            num_ids = [int(id) for id in self.context.keys()
                       if int_re.match(id) is not None] + [0]
            name = str(max(num_ids)+1)
        return name

    def checkName(self, name, message):
        int(name)
        return True
