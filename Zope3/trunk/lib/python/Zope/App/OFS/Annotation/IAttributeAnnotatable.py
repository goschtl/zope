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

$Id: IAttributeAnnotatable.py,v 1.3 2002/07/20 23:31:57 sidnei Exp $
"""
from IAnnotatable import IAnnotatable
from Interface.Attribute import Attribute

class IAttributeAnnotatable(IAnnotatable):
    """
    Marker interface giving permission for an IAnnotations adapter to store
    data in an attribute named __annotations__.
    """

    __annotations__ = Attribute(
        """
        This attribute may be used by an IAnnotations adapter to
        store pickleable data in.  The object implementing this
        interface promises not to touch the attribute other than
        to persist it.
        """)
