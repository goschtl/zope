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
Revision:
$Id: ContainerTraversable.py,v 1.2 2002/06/10 23:27:55 jim Exp $
"""


from Zope.App.Traversing.ITraversable import ITraversable
from Zope.App.Traversing.Exceptions import UnexpectedParameters
from IContainer import IReadContainer
from Zope.Exceptions import NotFoundError
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

_marker = object()

class ContainerTraversable:
    """Traverses containers via getattr and get.
    """

    __implements__ = ITraversable
    __used_for__ = IReadContainer

    def __init__(self, container):
        self._container = container


    def traverse(self, name, parameters, original_name, furtherPath):
        if parameters:
            raise UnexpectedParameters(parameters)

        container = self._container
        
        v = container.get(name, _marker)
        if v is _marker:
            v = getattr(container, name, _marker)
            if v is _marker:            
                raise NotFoundError, original_name

        return v

