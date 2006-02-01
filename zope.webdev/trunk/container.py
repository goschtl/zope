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
"""Content component for the resource container.

$Id$
"""
__docformat__ = "reStructuredText"

from zope.app.container.btree import BTreeContainer
from zope.interface import implements
from interfaces import IResourceContainer

class ResourceContainer(BTreeContainer):
    """A content type for holding resources.
    """
    implements(IResourceContainer)
    
    
    
