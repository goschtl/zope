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

$Id: IAttributeAnnotatable.py,v 1.4 2002/10/04 17:46:05 jim Exp $
"""
from IAnnotatable import IAnnotatable

class IAttributeAnnotatable(IAnnotatable):
    """
    Marker interface giving permission for an IAnnotations adapter to store
    data in an attribute named __annotations__.
    """
