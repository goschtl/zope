##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

$Id: IAnnotatable.py,v 1.2 2002/06/10 23:27:51 jim Exp $
"""
from Interface import Interface
from Interface.Attribute import Attribute

class IAnnotatable(Interface):
    """
    Marker interface for objects that support storing annotations.
    
    This interface says "There exists an adapter to an IAnnotations
    for an object that implements IAnnotatable".
    
    Classes should not directly declare that they implement this interface.
    Instead they should implement an interface derived from this one, which
    details how the annotations are to be stored, such as
    IAttributeAnnotatable.
    """
