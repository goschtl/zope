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
"""

Revision information: $Id: Addable.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""

"Keep track of add-menu contents"

from IAddable import IAddable

class Addable(object):
    
    __implements__=IAddable

    def __init__(self, id, title, description,
                 for_container=None,
                 creation_markers=None, icon=None):
        self.__id = id
        self.title = title
        self.description = description
        self.icon = icon
        self.for_container=for_container
        if creation_markers:
            if hasattr(self, "__implements__"): 
                # not checking to see if already there...
                self.__implements__ = creation_markers, self.__implements__
            else: self.__implements__=creation_markers

    def __getid(self): return self.__id
    
    id=property(__getid)
    
    def __eq__(self, other): # here basically just for unit tests...
        if not IAddable.isImplementedBy(other):
            return 0
        try:
            i, t, d = other.id, other.title, other.description
        except AttributeError:
            return 0
        
        return self.id == i and self.title == t and self.description == d
    
    def __repr__(self): # and for debugging
        return "<Addable %s (%s)>" % (self.__id, self.title)

    