##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Keep track of add-menu contents

Revision information: $Id: IAddable.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute


class IAddable(Interface):
    """objects that present a more human-readable front to factories."""
    
    def __init__(id, title, description, icon, createViewMarkers):
        """attributes as below, with createViewMarkers going into
        __mutable_implements__ (see IMutableInterfaceClass)"""
    
    id = Attribute (
        """the name that the factory services should recognize to create
        this kind of object.
        
        read-only, set in __init__.""")
    
    title = Attribute (
        """the human readable name for this type of addable: has no
        further significance
        
        read-write""")
    
    description = Attribute(
        """the human readable description for this type of addable: has
        no further significance.
        
        read-write""")
    
    icon = Attribute(
        """the icon for this addable type; implementation TBA (i.e.,
        name for view resource, actual image object, etc. unknown at
        this time)
        
        read-write""")
    
    for_container = Attribute(
        """the interfaces of objects that can contain this addable""")

    